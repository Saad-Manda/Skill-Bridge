# Skill-Bridge

## Scoring Resume

## **Skill Score System – Full Design**

### **1. Inputs**

* **JD Skills**: List of required skills from Job Description.

  * Each skill may have an optional **importance weight** (default = equal weight if not specified).
* **Resume Skills**: List of extracted skills from candidate resume.

  * Optionally, each skill may have a **proficiency level** (years of experience, seniority, certifications).
* **Embedding Model**: Pre-trained model (HuggingFace / sentence-transformers) to compute semantic similarity between skills.
* **Hyperparameters**:

  * `threshold`: minimum similarity to consider a match valid (e.g., 0.65–0.7)
  * `bonus_alpha`: weight of bonus score for resume-only relevant skills (0.1–0.3)
  * Optional: `max_bonus_cap` to limit effect of extra skills.

---

### **2. Skill Categorization**

For scoring purposes, classify skills into categories:

| Category                              | Description                                                                                                       |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **A. JD-only skills**                 | Skills required by JD but missing in resume. Should penalize.                                                     |
| **B. Matched skills**                 | Skills present in both JD and resume (direct or semantic match). Weighted positively.                             |
| **C. Resume-only relevant skills**    | Skills in resume not explicitly listed in JD but semantically related to JD skills. Add small bonus.              |
| **D. Resume-only irrelevant skills**  | Skills in resume unrelated to JD skills. Ignore.                                                                  |
| **E. Clustered / Many-to-One skills** | Multiple resume skills mapping to a single JD skill (e.g., ML → TensorFlow + scikit-learn). Aggregate similarity. |

---

### **3. Scoring Logic**

#### **Step 1: JD → Resume Mapping**

* Compute semantic similarity between each JD skill and all resume skills.
* **Aggregate matches for clustered skills**:

  * Option 1: Max similarity (`max(sim_jd_to_resume)`)
  * Option 2: Soft OR: `1 - ∏(1 - sim(r_i, jd_skill))` → captures multiple contributions but caps at 1.
* Apply **similarity threshold**:

  * If `sim < threshold`, treat as **missing skill** → similarity = 0.

---

#### **Step 2: Weighted Aggregation**

* Compute weighted sum of JD skills:
  [
  main_score = \frac{\sum (jd_weight * sim)}{\sum jd_weight}
  ]
* Missing JD skills reduce `main_score` because their similarity is zero.

---

#### **Step 3: Resume-Only Bonus**

* Identify **resume skills not mapped to any JD skill**.
* For each, compute **relevance** as max similarity to any JD skill.
* Include only skills with **relevance > threshold_bonus** (e.g., 0.7).
* Compute bonus as:
  [
  bonus = \alpha * \text{average(relevant resume-only similarities)}
  ]
* Add bonus to main_score, capped to prevent inflation.

---

#### **Step 4: Optional Adjustments**

* **Experience weighting**: multiply skill similarity by years of experience if available.
* **Proficiency scaling**: scale similarity by proficiency level (junior/intermediate/senior).
* **Skill importance overrides**: allow recruiter to mark certain JD skills as mandatory (weight = 1), others as nice-to-have (weight < 1).

---

### **4. Output**

Return a **structured result** that is directly usable by the dashboard:

| Field            | Description                                                             |
| ---------------- | ----------------------------------------------------------------------- |
| `skill_score`    | Final numeric score (0–1 or 0–100).                                     |
| `matched_skills` | Dictionary of JD skills → best matched resume skill(s) with similarity. |
| `missing_skills` | List of JD skills with no sufficient match.                             |
| `bonus_skills`   | Resume-only skills contributing to bonus score.                         |
| `breakdown`      | Optional detailed breakdown: similarity × weight per JD skill.          |

---

### **5. Edge Cases Covered**

1. **JD skills missing in resume** → penalized (score = 0 for that skill).
2. **Multiple resume skills matching one JD skill** → aggregated similarity (max or soft OR).
3. **Resume-only skills relevant to JD** → small bonus (controlled via `alpha`).
4. **Resume-only irrelevant skills** → ignored.
5. **Variable importance / weighting** → JD skills weighted according to importance.
6. **Low similarity matches** → filtered by threshold.
7. **Experience/proficiency consideration** → optional multiplier on similarity.
8. **Empty resume skills** → final skill score = 0.
9. **Empty JD skills** → undefined; can default to 1 or error.

---

### **6. Optional Enhancements**

* **Skill synonym expansion**: expand JD skills to include related concepts (ML → TensorFlow, scikit-learn, PyTorch).
* **Knowledge graph integration**: identify related skills automatically.
* **Gap analysis for career coaching**: highlight missing JD skills to the candidate.

---

### Example

#### **Job Description (JD) Skills and Weights**
| Skill | Weight |
|-------|--------|
| Python | 0.3 |
| Machine Learning | 0.4 |
| AWS | 0.2 |
| Data Visualization | 0.1 |

#### **Candidate Resume Skills**
- Python  
- TensorFlow  
- scikit-learn  
- Docker  

---

### **Step 1: Categorize Skills**

1. **Matched / Clustered Skills** (JD skill present in resume or related skills)  
   - Machine Learning → TensorFlow, scikit-learn  
   - Python → Python  

2. **JD-only skills missing**  
   - AWS  
   - Data Visualization  

3. **Resume-only relevant skills**  
   - Docker (related to AWS/DevOps)  

4. **Resume-only irrelevant skills**  
   - None in this example  

---

### **Step 2: Compute Similarity (Semantic Matching)**

- Python → Python = **1.0** (direct match)  
- Machine Learning → TensorFlow, scikit-learn = **aggregate similarity** 0.82 (soft OR of both)  
- AWS → No match → **0** (missing skill)  
- Data Visualization → No match → **0** (missing skill)  

Resume-only skill (Docker) has **relevance to AWS** = 0.6 → below bonus threshold → ignored for bonus.

---

### **Step 3: Weighted Aggregation**

Weighted sum of JD skills:  
\[
SkillScore_{main} = (0.3*1.0) + (0.4*0.82) + (0.2*0) + (0.1*0) = 0.3 + 0.328 + 0 + 0 = 0.628
\]  
Divide by total weight (1.0) → **0.628**

---

### **Step 4: Resume-only Bonus**

- No bonus because Docker similarity to JD skills < 0.7 threshold.  
- Bonus = 0  

---

### **Step 5: Final Skill Score**

\[
SkillScore = MainScore + Bonus = 0.628 + 0 = 0.628
\]  
**Final Score: 62.8%**

---

### **Step 6: Output (Structured)**

```json
{
  "skill_score": 0.628,
  "matched_skills": {
      "Python": ["Python"],
      "Machine Learning": ["TensorFlow", "scikit-learn"]
  },
  "missing_skills": ["AWS", "Data Visualization"],
  "bonus_skills": []
}
```

---

### ✅ **Summary of Cases Covered**

| Case | Example | How Handled |
|------|---------|-------------|
| JD skill missing in resume | AWS | similarity=0 → penalizes score, appears in missing_skills |
| JD skill matched (direct) | Python | similarity=1 → full weight applied |
| JD skill matched via cluster | Machine Learning → TensorFlow + scikit-learn | aggregate similarity applied |
| Resume-only relevant skill | Docker | similarity < threshold → ignored for bonus (if ≥ threshold, small bonus added) |
| Resume-only irrelevant skill | (none) | ignored |
| Weighted JD skills | All skills have weights | used in main score calculation |

---

This example clearly shows how:  
1. Missing JD skills reduce the score.  
2. Clustered skills are handled together.  
3. Resume-only relevant skills can optionally add small bonus.  
4. Final score is a weighted combination — not a simple average.  

---