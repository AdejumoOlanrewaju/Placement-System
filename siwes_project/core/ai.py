import json
from groq import Groq
from django.conf import settings

def generate_recommendations(student, listings):
    """
    Takes a StudentProfile and a queryset of PlacementListings.
    Returns a list of dicts: [{listing_id, score, reason}, ...]
    sorted by score descending.
    """

    client = Groq(api_key=settings.GROQ_API_KEY)

    # --- BUild the student context ---
    student_context = {
        "full_name"      : student.user.get_full_name(),
        "department"     : student.department,
        "institution"    : student.institution,
        "skills"         : student.skills or "Not specified",
        "preferred_state": str(student.preferred_state) if student.preferred_state else "Not specified",
        "preferred_lga"  : str(student.preferred_lga)   if student.preferred_lga   else "Not specified",
    }

    # ── Build listings context ──
    listings_context = []
    for listing in listings:
        listings_context.append({
            "id"                 : listing.id,
            "title"              : listing.title,
            "company"            : listing.company.company_name,
            "industry"           : listing.company.industry,
            "department_required": listing.department_required,
            "skills_required"    : listing.skills_required or "Not specified",
            "state"              : str(listing.state),
            "lga"                : str(listing.lga),
            "description"        : listing.description[:300],
        })
    
    if not listings_context:
        return []
    
    prompt = f"""
You are a SIWES placement advisor helping a Nigerian university student find the best industrial training placement.

STUDENT PROFILE:
{json.dumps(student_context, indent=2)}

AVAILABLE LISTINGS:
{json.dumps(listings_context, indent=2)}

TASK:
Analyze each listing and rank them by how well they match the student's profile.
Consider:
1. Department/field match (most important)
2. Location match (state and LGA proximity)
3. Skills match
4. Industry relevance

Return a JSON array ONLY — no explanation outside the JSON.
Each object must have exactly these fields:
- "listing_id": (integer) the id of the listing
- "score": (float between 0 and 1) how well it matches
- "reason": (string, max 2 sentences) why this listing suits this student

Sort by score descending. Include ALL listings with a score above 0.3.
Return ONLY the JSON array, no markdown, no backticks, no explanation.

Example format:
[
  {{"listing_id": 1, "score": 0.95, "reason": "Your Computer Science background directly matches the required department. The company is located in your preferred state."}},
  {{"listing_id": 2, "score": 0.72, "reason": "Your Python skills align with the requirements. Located slightly outside your preferred area."}}
]
"""
    
    try:
        response = client.chat.completions.create(
            model    = "llama-3.3-70b-versatile",
            messages = [{"role": "user", "content": prompt}],
            max_tokens      = 1500,
            temperature     = 0.3,
        )

        raw     = response.choices[0].message.content.strip()
        # strip any accidental markdown fences
        raw     = raw.replace("```json", "").replace("```", "").strip()
        results = json.loads(raw)

        # validate structure
        validated = []
        for item in results:
            if all(k in item for k in ["listing_id", "score", "reason"]):
                validated.append({
                    "listing_id": int(item["listing_id"]),
                    "score"     : float(item["score"]),
                    "reason"    : str(item["reason"]),
                    "percentage"  : f"{float(item['score'])*100:.0f}"
                })

        return sorted(validated, key=lambda x: x["score"], reverse=True)

    except (json.JSONDecodeError, Exception):
        return []


