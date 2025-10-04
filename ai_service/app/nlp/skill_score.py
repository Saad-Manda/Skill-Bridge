from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def load_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    return SentenceTransformer(model_name)


def compute_embeddings(skills: List[str], model: SentenceTransformer) -> np.ndarray:
    if not skills:
        return np.array([])
    return model.encode(skills, convert_to_numpy=True)



def compute_jd_weights(
    title: str,
    skill_embedding: List[str],
    model: SentenceTransformer,
    responsibilities: List[str] = [],
    title_boost: float = 1.2,
    responsibility_boost: float = 0.1,
    normalize: bool = True
) -> Dict[str, float]:

    if not skill_embedding:
        return {}
    
    title_embedding = compute_embeddings([title], model)[0]

    weights = {skill: 1.0 for skill in skill_embedding}

    
    for i, skill in enumerate(skill_embedding):
        skill_vec = skill_embedding[i]

        sim = np.dot(skill_vec, title_embedding) / (np.linalg.norm(skill_vec) * np.linalg.norm(title_embedding))

        if sim > 0.5:
            weights[skill] *= title_boost


    if responsibilities:
        resp_embeddings = compute_embeddings(responsibilities, model)

        for i, skill in enumerate(skill_embedding):
            skill_vec = skill_embedding[i]
            
            max_sim = max(
                np.dot(skill_vec, r_vec) / (np.linalg.norm(skill_vec) * np.linalg.norm(r_vec))
                for r_vec in resp_embeddings
            )
            if max_sim > 0.5:
                weights[skill] += responsibility_boost * max_sim


    if normalize:
        total = sum(weights.values())
        weights = {skill: w / total for skill, w in weights.items()}

    return weights



def compute_similarity_matrix(jd_embeddings: np.ndarray, resume_embeddings: np.ndarray) -> np.ndarray:
    if jd_embeddings.size == 0 or resume_embeddings.size == 0:
        return np.zeros((jd_embeddings.shape[0], resume_embeddings.shape[0]))
    
    return cosine_similarity(jd_embeddings, resume_embeddings)



def map_jd_to_resume(
    jd_skills: List[str],
    resume_skills: List[str],
    jd_weights: Dict[str, float],
    similarity_matrix: np.ndarray,
    threshold: float = 0.65
) -> Tuple[Dict[str, List[str]], List[str], Dict[str, float]]:

    matched_skills = {}
    missing_skills = []
    jd_sim_scores = {}

    for i, jd_skill in enumerate(jd_skills):
        if resume_skills:
            sims = similarity_matrix[i]
            max_sim = sims.max()
            
            relevant_indices = [j for j, s in enumerate(sims) if s >= threshold]
            if relevant_indices:
                matched_skills[jd_skill] = [resume_skills[j] for j in relevant_indices]
                jd_sim_scores[jd_skill] = max_sim
            else:
                matched_skills[jd_skill] = []
                missing_skills.append(jd_skill)
                jd_sim_scores[jd_skill] = 0.0
        else:
            matched_skills[jd_skill] = []
            missing_skills.append(jd_skill)
            jd_sim_scores[jd_skill] = 0.0

    return matched_skills, missing_skills, jd_sim_scores



def compute_resume_only_bonus(
    jd_skills: List[str],
    resume_skills: List[str],
    similarity_matrix: np.ndarray,
    alpha: float = 0.2,
    bonus_threshold: float = 0.7
) -> List[str]:
    
    bonus_skills = []

    if not resume_skills or not jd_skills:
        return bonus_skills

    num_jd = len(jd_skills)
    num_resume = len(resume_skills)

    for j in range(num_resume):
        max_rel = similarity_matrix[:, j].max()
        if max_rel >= bonus_threshold:
            bonus_skills.append(resume_skills[j])

    return bonus_skills



def compute_weighted_skill_score(
    jd_weights: Dict[str, float],
    jd_sim_scores: Dict[str, float],
    alpha: float,
    bonus_count: int,
    total_resume_skills: int
) -> float:
    
    main_score = sum(jd_weights[jd]*jd_sim_scores[jd] for jd in jd_weights) / sum(jd_weights.values())


    if total_resume_skills > 0 and bonus_count > 0:
        bonus_score = alpha * (bonus_count / total_resume_skills)
    else:
        bonus_score = 0.0


    final_score = main_score + bonus_score

    return round(min(final_score, 1.0), 3)



def compute_skill_score(
    jd_skills: List[str],
    resume_skills: List[str],
    jd_title: str,
    jd_responsiblities: List[str] = [],
    jd_weights: Dict[str, float] = None,
    model_name: str = "all-MiniLM-L6-v2",
    threshold: float = 0.65,
    bonus_threshold: float = 0.7,
    alpha: float = 0.2
) -> Dict:

    model = load_embedding_model(model_name)
    jd_embeddings = compute_embeddings(jd_skills, model)
    resume_embeddings = compute_embeddings(resume_skills, model)


    if jd_weights is None:
        jd_weights = compute_jd_weights(jd_title, jd_embeddings, model, jd_responsiblities)


    sim_matrix = compute_similarity_matrix(jd_embeddings, resume_embeddings)


    matched_skills, missing_skills, jd_sim_scores = map_jd_to_resume(
        jd_skills, resume_skills, jd_weights, sim_matrix, threshold
    )


    bonus_skills = compute_resume_only_bonus(
        jd_skills, resume_skills, sim_matrix, alpha, bonus_threshold
    )


    final_score = compute_weighted_skill_score(
        jd_weights, jd_sim_scores, alpha, len(bonus_skills), len(resume_skills)
    )

    return {
        "skill_score": final_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "bonus_skills": bonus_skills
    }