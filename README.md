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


# Skill Scoring Algorithm

1. **Undirected Edges are Insufficient:** You cannot rely on undirected co-occurrence. "PyTorch" implies "Python", but "Python" does not imply "PyTorch". If a JD asks for Python and I have PyTorch, I should match. If a JD asks for PyTorch and I only have Python, I should fail. Your current graph treats them as equals.
2. **The "Capability Layer" is Operational Debt:** Manually maintaining "capability tags" (analytics, infra, etc.) for 10,000+ rapidly changing skills is impossible. You will drown in maintenance. The graph structure itself must solve this.
3. **Ambiguous Scoring:** "Penalize" and "Reward" are too vague. You need a normalized mathematical framework, otherwise, your scores will drift (e.g., a candidate with 100 irrelevant skills might outscore a focused candidate simply by accumulating tiny "Category C" bonuses).

---

# Directed Skill Implication Graph (DSIG)

### Core Philosophy Shift

We are moving from a **Co-occurrence Graph** (undirected, "A is related to B") to an **Implication Graph** (directed, "B implies proficiency in A").

## 1. The Data Structure (What We Store)

We do not store a monolithic adjacency matrix. We store a **Knowledge Graph** with two specific node types and embedding support.

### 1.1 Node Schema

Each node represents a Skill.

```json
{
  "id": "skill_123",
  "canonical_name": "PostgreSQL",
  "type": "SKILL",
  "cluster_id": 12,  // From offline community detection (e.g., "Relational DBs")
  "popularity_score": 0.85, // 0 to 1 (Global frequency)
  "embedding": [0.12, -0.45, ...] // S-BERT vector of the skill description/context
}

```

### 1.2 Edge Schema

We store two types of edges. This is critical for the "Directionality" problem.

| Edge Type | Direction | Meaning | Weight |
| --- | --- | --- | --- |
| **CO_OCCUR** | Undirected | "People often have both" |  |
| **IMPLIES** | Directed () | "Knowing A strongly implies knowing B" | $P(B |

*Example:*

* `PyTorch` -> **IMPLIES** (0.95) -> `Python`
* `Python` -> **IMPLIES** (0.05) -> `PyTorch` (Weak edge, pruned)
* `React` <-> **CO_OCCUR** <-> `Node.js` (Strong ecosystem overlap, but one doesn't strictly imply the other)

---

## 2. Offline Phase: Graph Construction

We automate the "Capability" check using vectors and conditional probability, removing the manual tagging need.

**Step 1: Metric Calculation**
For every pair  in the resume corpus:

1. **Co-occurrence:** Jaccard Index.
2. **Implication:** Calculate Conditional Probability .
* *If  is high (> 0.7) and  is low*, create a directed **IMPLIES** edge from A to B.
* *If both are roughly equal and high*, create a **CO_OCCUR** edge.



**Step 2: Semantic Guardrails (The "Anti-Redis-Analytics" Check)**
Before saving an edge, compute the **Cosine Similarity** between the embeddings of Skill A and Skill B.

* If `EdgeWeight` is high but `VectorSimilarity` is low (e.g., "Java" and "Recruiting" often appear together in HR tech resumes), **PRUNE THE EDGE**. This automatically filters buzzword noise without manual tags.

**Step 3: Community Detection**
Run Louvain/Leiden on the graph. Store the `ClusterID` on every node. This replaces your "Capability Layer." If Node A and Node B are in different clusters, they are functionally distinct.

---

## 3. Runtime Phase: The Matching Algorithm

This is the exact logical flow to code.

### Inputs

* ****: Set of Skills in Job Description (weighted by explicit "Required" vs "Nice to have").
* ****: Set of Skills in Resume.

### Step 3.1: Expand the JD (The "Query Subgraph")

We don't just look for the JD skills. We look for what they *imply* and what they are *part of*.

For each skill :

1. Fetch  from the graph.
2. **Expansion A (Alternatives):** Fetch neighbors connected via strong **CO_OCCUR** edges (e.g., JD asks for "AWS", graph suggests "Azure" is a valid alternative/context).
3. **Expansion B (Children):** Fetch nodes that **IMPLY**  (e.g., JD asks for "Python"; graph knows "Django" implies "Python").

This creates a localized subgraph .

### Step 3.2: Classify Resume Skills

Iterate through every skill  and map it against :

| Relationship to JD Skill () | Classification | Scoring Logic |
| --- | --- | --- |
|  | **Direct Match** | Max Score (1.0) |
|  | **Deep Match** | High Score (1.0) (e.g. JD: Python, Res: PyTorch) |
|  | **Broad Match** | Partial Score (0.5) (e.g. JD: PyTorch, Res: Python) |
|  | **Adjacent** | Low Score (0.2 - 0.4) based on weight |
| Same Cluster, No Edge | **Thematic** | Tiny Bonus (0.05) |
| Different Cluster | **Irrelevant** | 0.0 |

---

## 4. The Final Scoring Formula

We need a unified score, not just buckets.

Let  be the weight of a JD skill (e.g., 1.0 for required, 0.5 for optional).
Let  be the best match score for JD skill  found in the resume.

### Handling the "Categories" (A-E)

**Category A (Missing Critical Skills):**
Handled by the denominator. If you miss a high  skill, your max possible score drops significantly.

* *Refinement:* Apply a **Non-Linear Penalty**. If coverage of "Required" skills < 50%, multiply final score by 0.5.

**Category B (Matches):**
Handled by "Direct Match" and "Deep Match" logic ().

**Category C (Relevant Bonus):**
Handled by "Adjacent" logic. If JD wants "Postgres" and you have "MySQL" (strong co-occur/cluster match), you get 0.3 points. This boosts you over a candidate with nothing, but keeps you below a perfect match.

**Category D (Irrelevant):**
Filtered naturally. If a skill isn't in  (the subgraph) and isn't in the same cluster, it contributes 0 to the numerator.

**Category E (Many-to-One):**
We use a `Max()` function per JD skill bucket.

* If JD asks for "AWS" ().
* Resume has "EC2", "S3", "Lambda".
* All three imply "AWS".
* We do not sum them (which would explode the score). We take . You can saturate the "AWS" requirement, but you cannot exceed it to compensate for missing "Python".

---

## 5. Summary of Improvements

1. **Fixed Directionality:** "Deep Matches" (I have PyTorch, you asked for Python) are now mathematically distinct from "Broad Matches".
2. **Removed Manual Tags:** Used **Vectors + Community Detection** to automate the "Context/Capability" layer.
3. **Bounded Scoring:** The score is a rigorous percentage () representing "Percentage of Job Requirements Met", rather than an arbitrary integer.
4. **Implicit vs Explicit:** We distinguish between explicitly asked skills and implicit gap filling using the **IMPLIES** edge type.

This system is defensible because every match is traceable to a specific edge in the graph, and the graph is built on statistically significant real-world data, not manual rules.
