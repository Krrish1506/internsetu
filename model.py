import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score

# ---------------------------
# LOAD DATA
# ---------------------------
students = pd.read_csv("student dataset.csv")       # ✅ same folder
companies = pd.read_csv("company dataset.csv")  # ✅ same folder

# Merge students with companies
students['key'] = 1
companies['key'] = 1
data = students.merge(companies, on='key').drop('key', axis=1)

# Target function
def qualifies(row):
    student_skills = str(row['skills']).lower().split(',')
    required_skills = str(row['skills_required']).lower().split(',')
    skills_match = all(skill.strip() in student_skills for skill in required_skills)
    cgpa_match = row['cgpa'] >= row['min_cgpa']
    projects_match = row['projects'] >= row['min_projects']
    return int(skills_match and cgpa_match and projects_match)

data['qualified'] = data.apply(qualifies, axis=1)

# Encode categorical features
le_dept = LabelEncoder()
data['department'] = le_dept.fit_transform(data['department'])
le_company = LabelEncoder()
data['company'] = le_company.fit_transform(data['company'])

# Features + Target
X = data[['department', 'cgpa', 'projects', 'min_cgpa', 'min_projects']]
y = data['qualified']

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ---------------------------
# TRAIN MODELS
# ---------------------------
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42)
}

best_model = None
best_acc = 0

for name, model in models.items():
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    if acc > best_acc:
        best_acc = acc
        best_model = model

print(f"\n✅ Best Model Selected: {type(best_model).__name__} with Accuracy = {best_acc:.3f}")

# ---------------------------
# SAVE TRAINED MODEL
# ---------------------------
with open("best_model.pkl", "wb") as f:
    pickle.dump(best_model, f)

with open("label_encoders.pkl", "wb") as f:
    pickle.dump({"dept": le_dept, "company": le_company}, f)

# ---------------------------
# PREDICTION FUNCTION
# ---------------------------
def recommend_for_new_student(student_profile, companies, model, le_dept, threshold=0.5):
    recommendations = []
    for _, comp in companies.iterrows():
        row = {
            'department': le_dept.transform([student_profile['department']])[0],
            'cgpa': student_profile['cgpa'],
            'projects': student_profile['projects'],
            'min_cgpa': comp['min_cgpa'],
            'min_projects': comp['min_projects']
        }
        df_row = pd.DataFrame([row])

        prob = model.predict_proba(df_row)[0][1] if hasattr(model, "predict_proba") else float(model.predict(df_row)[0])
        if prob >= threshold:
            recommendations.append((comp['company'], round(prob * 100, 2)))

    recommendations.sort(key=lambda x: x[1], reverse=True)
    return recommendations if recommendations else [("None", 0.0)]


# ---------------------------
# TEST EXAMPLE
# ---------------------------
if __name__ == "__main__":
    new_student = {
        "department": "CSE",
        "cgpa": 8.5,
        "projects": 3,
        "skills": "python,java"
    }

    recs = recommend_for_new_student(new_student, companies, best_model, le_dept)
    print("\n🎯 Recommended Companies:")
    for company, prob in recs:
        print(f"- {company}: {prob}% chance")
