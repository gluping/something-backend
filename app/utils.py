from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password:str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_pass):
    return pwd_context.verify(plain_password, hashed_pass)


def calculate_calories_for_weight_gain(weight, height):
    # Logic to calculate calorie intake for weight gain
    # Implement your own formula or use existing libraries for this calculation
    # Example code:
    bmr = 10 * weight + 6.25 * height - 5 * 20 + 5
    tdee = bmr *1.55
    calorie_intake = tdee + 500

    return calorie_intake


def calculate_calories_for_weight_loss(weight, height):
    # Logic to calculate calorie intake for weight loss
    # Implement your own formula or use existing libraries for this calculation
    # Example code:
    bmr = 10 * weight + 6.25 * height - 5 * 20 + 5
    tdee = bmr *1.55
    calorie_intake = tdee - 500

    return calorie_intake


def retrieve_diet_recommendations(goal):
    # Logic to retrieve diet recommendations based on the goal
    # Implement your own logic to retrieve diet recommendations from the database or any other source
    # Example code:
    if goal == "gain":
        diet_recommendations = ["Eat more protein", "Consume healthy fats", "Increase calorie intake"]
    elif goal == "lose":
        diet_recommendations = ["Eat more vegetables and fruits", "Reduce processed food intake", "Control portion sizes"]
    else:
        diet_recommendations = []

    return diet_recommendations


def retrieve_exercise_recommendations(goal):
    # Logic to retrieve exercise recommendations based on the goal
    # Implement your own logic to retrieve exercise recommendations from the database or any other source
    # Example code:
    if goal == "gain":
        exercise_recommendations = ["Strength training exercises", "Compound movements", "Progressive overload"]
    elif goal == "lose":
        exercise_recommendations = ["Cardiovascular exercises", "High-intensity interval training (HIIT)", "Regular physical activity"]
    else:
        exercise_recommendations = []

    return exercise_recommendations
