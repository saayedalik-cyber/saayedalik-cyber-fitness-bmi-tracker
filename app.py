import streamlit as st
import pandas as pd
import os
from datetime import datetime
import math

# ============================================================================
# Core BMI Functions
# ============================================================================

def calculate_bmi(weight_kg, height_m):
    return weight_kg / (height_m ** 2)

def get_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Healthy weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def healthy_weight_range(height_m):
    min_weight = 18.5 * (height_m ** 2)
    max_weight = 25 * (height_m ** 2)
    return min_weight, max_weight

# ============================================================================
# Unit Conversions
# ============================================================================

def lbs_to_kg(lbs):
    return lbs * 0.453592

def inches_to_m(inches):
    return inches * 0.0254

def feet_inches_to_m(feet, inches):
    total_inches = (feet * 12) + inches
    return inches_to_m(total_inches)

# ============================================================================
# BMR / TDEE Functions
# ============================================================================

ACTIVITY_LEVELS = {
    "Sedentary (little/no exercise)": 1.2,
    "Lightly active (1-3 days/week)": 1.375,
    "Moderately active (3-5 days/week)": 1.55,
    "Very active (6-7 days/week)": 1.725,
    "Athlete (2x/day training)": 1.9,
}

def calculate_bmr(weight_kg, height_m, age, gender):
    height_cm = height_m * 100
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    if gender == "Male":
        return base + 5
    else:
        return base - 161

def calculate_tdee(bmr, activity_multiplier):
    return bmr * activity_multiplier

def suggest_calorie_goals(tdee):
    return {
        "Mild weight loss (-0.25kg/week)": tdee - 275,
        "Weight loss (-0.5kg/week)": tdee - 550,
        "Maintain weight": tdee,
        "Weight gain (+0.25kg/week)": tdee + 275,
        "Muscle gain (+0.5kg/week)": tdee + 550,
    }

def suggest_macros(calorie_target):
    protein_cals = calorie_target * 0.30
    carb_cals = calorie_target * 0.35
    fat_cals = calorie_target * 0.35
    return {
        "Protein": protein_cals / 4,
        "Carbs": carb_cals / 4,
        "Fat": fat_cals / 9,
    }

def calculate_water_intake(weight_kg, activity_multiplier):
    base_liters = (weight_kg * 33) / 1000
    if activity_multiplier >= 1.55:
        base_liters += 0.5
    return base_liters

# ============================================================================
# History Management
# ============================================================================

HISTORY_FILE = "bmi_history.txt"

def save_to_history(name, bmi, category):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"{name} | {timestamp} | BMI: {bmi:.1f} | Category: {category}\n"
    with open(HISTORY_FILE, "a") as f:
        f.write(line)

def load_history():
    grouped = {}
    if not os.path.exists(HISTORY_FILE):
        return grouped
    with open(HISTORY_FILE, "r") as f:
        lines = f.readlines()
    for line in lines:
        parts = line.strip().split(" | ", 1)
        if len(parts) == 2:
            name, rest = parts
            grouped.setdefault(name, []).append(rest)
    return grouped

# ============================================================================
# Workout Plans
# ============================================================================

WORKOUT_PLANS = {
    ("Underweight", "build"): [
        "Focus: strength training 3-4x/week, compound lifts (squat, deadlift, bench, row)",
        "Keep cardio light (2-3 short sessions/week) so it doesn't eat into recovery",
        "Prioritize progressive overload - add a little weight or a rep each week",
    ],
    ("Healthy weight", "maintain"): [
        "Mix of strength (2-3x/week) and cardio (2-3x/week) for balanced fitness",
        "Include mobility/flexibility work (yoga, stretching) 1-2x/week",
        "Try a new activity each month to keep things interesting",
    ],
    ("Healthy weight", "build"): [
        "Strength training 4x/week with a slight calorie surplus",
        "Push progressive overload on major lifts",
        "1-2 light cardio sessions/week for heart health, not fat loss",
    ],
    ("Overweight", "lose"): [
        "Combine strength training (2-3x/week) with cardio (3-4x/week)",
        "Start with low-impact cardio (walking, cycling, swimming) if joints are a concern",
        "Aim for a moderate calorie deficit alongside the activity, not the deficit alone",
    ],
    ("Obese", "lose"): [
        "Start with low-impact activity: walking, swimming, stationary bike",
        "Add bodyweight strength work 2x/week once cardio feels comfortable",
        "Small consistent sessions (20-30 min) beat occasional long ones early on",
        "Consider checking in with a doctor before starting a new intense routine",
    ],
}

def get_workout_plan(category, goal):
    key = (category, goal)
    if key in WORKOUT_PLANS:
        return WORKOUT_PLANS[key]
    # Fallback
    if goal == "lose":
        return WORKOUT_PLANS.get(("Overweight", "lose"), ["Start with walking and light activity"])
    elif goal == "build":
        return WORKOUT_PLANS.get(("Healthy weight", "build"), ["Focus on strength training"])
    else:
        return WORKOUT_PLANS.get(("Healthy weight", "maintain"), ["Mix of strength and cardio"])

# ============================================================================
# Streamlit App
# ============================================================================

st.set_page_config(
    page_title="BMI & Fitness Toolkit",
    page_icon="💪",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .bmi-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .category-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .underweight { background-color: #FFB74D; color: #333; }
    .healthy { background-color: #81C784; color: #333; }
    .overweight { background-color: #FFD54F; color: #333; }
    .obese { background-color: #EF5350; color: white; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">💪 BMI & Fitness Toolkit</div>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("📋 Menu")
app_mode = st.sidebar.radio(
    "Choose a tool:",
    ["BMI Calculator", "Fitness Calculator", "Workout Planner", "History", "Progress Trend"]
)

# ============================================================================
# BMI Calculator
# ============================================================================

if app_mode == "BMI Calculator":
    st.header("📊 BMI Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Your Name", placeholder="Enter your name")
        
        unit_system = st.radio("Choose unit system:", ["Metric (kg, m)", "Imperial (lbs, ft/in)"])
        
        if unit_system == "Metric (kg, m)":
            weight = st.number_input("Weight (kg)", min_value=1.0, step=0.1, value=70.0)
            height = st.number_input("Height (m)", min_value=0.5, step=0.01, value=1.75)
        else:
            weight_lbs = st.number_input("Weight (lbs)", min_value=2.0, step=0.1, value=154.0)
            feet = st.number_input("Height - Feet", min_value=1, step=1, value=5)
            inches = st.number_input("Height - Inches", min_value=0, max_value=11, step=1, value=9)
            weight = lbs_to_kg(weight_lbs)
            height = feet_inches_to_m(feet, inches)
        
        add_waist = st.checkbox("Also check Waist-to-Height ratio?")
        if add_waist:
            waist_cm = st.number_input("Waist measurement (cm)", min_value=20.0, step=0.1, value=80.0)
        
        calculate_btn = st.button("Calculate BMI", type="primary", use_container_width=True)
    
    if calculate_btn:
        if not name:
            name = "Unknown"
        
        bmi = calculate_bmi(weight, height)
        category = get_category(bmi)
        min_w, max_w = healthy_weight_range(height)
        
        with col2:
            st.markdown(f"""
            <div class="bmi-card">
                <h3>Your Results</h3>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Weight:</strong> {weight:.1f} kg</p>
                <p><strong>Height:</strong> {height:.2f} m</p>
                <p><strong>BMI:</strong> <span style="font-size: 2rem; font-weight: bold;">{bmi:.1f}</span></p>
                <div class="category-badge {category.lower().replace(' ', '')}">{category}</div>
                <p><strong>Healthy weight range:</strong> {min_w:.1f} kg - {max_w:.1f} kg</p>
            </div>
            """, unsafe_allow_html=True)
            
            if add_waist:
                ratio = waist_cm / (height * 100)
                if ratio < 0.5:
                    note = "✅ Generally considered a healthy ratio"
                else:
                    note = "⚠️ Above the commonly used 0.5 healthy threshold"
                st.info(f"**Waist-to-Height Ratio:** {ratio:.2f}\n{note}")
            
            # Save to history
            save_to_history(name, bmi, category)
            
            # Diet suggestions
            st.markdown("### 🥗 General Diet Suggestions")
            if category == "Underweight":
                st.info("""
                - Consider adding nutrient-dense snacks like nuts, yogurt, or whole grains
                - Eating a bit more frequently through the day can help
                - Protein at each meal supports healthy weight gain
                """)
            elif category == "Healthy weight":
                st.success("""
                - Focus on consistency and variety in your diet
                - Keep a good mix of vegetables, protein, and whole grains
                - Stay mindful of sugary drinks
                """)
            elif category == "Overweight":
                st.warning("""
                - Try adding more vegetables and fiber to meals
                - Cut back on sugary drinks and fried snacks
                - Regular movement pairs well with diet changes
                """)
            else:  # Obese
                st.error("""
                - Small, gradual changes tend to stick better than drastic ones
                - Reducing processed/fried food and sugary drinks is a good start
                - Consider speaking to a doctor or nutritionist for a personal plan
                """)
            
            # Workout offer
            if st.button("💪 Get Workout Plan"):
                st.session_state.workout_category = category
                st.session_state.show_workout = True

# ============================================================================
# Fitness Calculator
# ============================================================================

elif app_mode == "Fitness Calculator":
    st.header("🔥 Fitness & Nutrition Calculator")
    st.markdown("Calculate BMR, TDEE, calorie goals, macros, and water intake")
    
    col1, col2 = st.columns(2)
    
    with col1:
        unit_system = st.radio("Unit system:", ["Metric (kg, m)", "Imperial (lbs, ft/in)"], key="fitness_units")
        
        if unit_system == "Metric (kg, m)":
            weight = st.number_input("Weight (kg)", min_value=1.0, step=0.1, value=70.0, key="f_weight")
            height = st.number_input("Height (m)", min_value=0.5, step=0.01, value=1.75, key="f_height")
        else:
            weight_lbs = st.number_input("Weight (lbs)", min_value=2.0, step=0.1, value=154.0, key="f_weight_lbs")
            feet = st.number_input("Height - Feet", min_value=1, step=1, value=5, key="f_feet")
            inches = st.number_input("Height - Inches", min_value=0, max_value=11, step=1, value=9, key="f_inches")
            weight = lbs_to_kg(weight_lbs)
            height = feet_inches_to_m(feet, inches)
        
        age = st.number_input("Age", min_value=10, max_value=120, step=1, value=30)
        gender = st.radio("Sex", ["Male", "Female"])
        
        activity = st.selectbox(
            "Activity Level",
            list(ACTIVITY_LEVELS.keys())
        )
        activity_multiplier = ACTIVITY_LEVELS[activity]
        
        calc_btn = st.button("Calculate Fitness Metrics", type="primary", use_container_width=True)
    
    if calc_btn:
        bmr = calculate_bmr(weight, height, age, gender)
        tdee = calculate_tdee(bmr, activity_multiplier)
        goals = suggest_calorie_goals(tdee)
        water = calculate_water_intake(weight, activity_multiplier)
        
        with col2:
            st.markdown(f"""
            <div class="bmi-card">
                <h3>Your Fitness Metrics</h3>
                <p><strong>BMR (Calories at rest):</strong> {bmr:.0f} kcal/day</p>
                <p><strong>Activity Level:</strong> {activity}</p>
                <p><strong>TDEE (Maintain weight):</strong> {tdee:.0f} kcal/day</p>
                <p><strong>💧 Water Intake:</strong> {water:.1f} L ({water*33.8:.0f} fl oz)</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🎯 Calorie Goals by Target")
            goal_data = []
            for goal_name, cals in goals.items():
                goal_data.append({"Goal": goal_name, "Calories": f"{cals:.0f} kcal/day"})
            st.dataframe(pd.DataFrame(goal_data), hide_index=True, use_container_width=True)
            
            # Macro breakdown
            st.markdown("### 📊 Macro Breakdown")
            
            # Let user select a goal to see macros
            goal_options = list(goals.keys())
            selected_goal = st.selectbox("Select a goal for macro breakdown:", goal_options)
            selected_cals = goals[selected_goal]
            macros = suggest_macros(selected_cals)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Protein", f"{macros['Protein']:.0f}g", f"{macros['Protein']*4:.0f} kcal")
            with col_b:
                st.metric("Carbs", f"{macros['Carbs']:.0f}g", f"{macros['Carbs']*4:.0f} kcal")
            with col_c:
                st.metric("Fat", f"{macros['Fat']:.0f}g", f"{macros['Fat']*9:.0f} kcal")
            
            # Body fat estimate
            if st.checkbox("Estimate Body Fat % (requires measurements)"):
                st.markdown("### 📏 Body Fat Estimate (US Navy Method)")
                height_cm = height * 100
                waist = st.number_input("Waist (cm)", min_value=20.0, step=0.1, value=80.0)
                neck = st.number_input("Neck (cm)", min_value=20.0, step=0.1, value=35.0)
                hip = None
                if gender == "Female":
                    hip = st.number_input("Hip (cm)", min_value=20.0, step=0.1, value=95.0)
                
                if hip is not None:  # Female
                    bf = 495 / (1.29579 - 0.35004 * math.log10(waist + hip - neck) + 0.22100 * math.log10(height_cm)) - 450
                else:  # Male
                    bf = 495 / (1.0324 - 0.19077 * math.log10(waist - neck) + 0.15456 * math.log10(height_cm)) - 450
                
                st.info(f"**Estimated Body Fat:** {bf:.1f}%")
                st.caption("US Navy tape-measure method - a rough estimate, not a DEXA scan.")

# ============================================================================
# Workout Planner
# ============================================================================

elif app_mode == "Workout Planner":
    st.header("💪 Workout Plan Suggestions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        know_bmi = st.radio("Do you know your BMI category?", ["Yes", "No"])
        
        if know_bmi == "Yes":
            category = st.selectbox("Select your BMI category:", ["Underweight", "Healthy weight", "Overweight", "Obese"])
        else:
            st.markdown("Enter your details to calculate BMI:")
            unit_system = st.radio("Unit system:", ["Metric (kg, m)", "Imperial (lbs, ft/in)"], key="workout_units")
            
            if unit_system == "Metric (kg, m)":
                w = st.number_input("Weight (kg)", min_value=1.0, step=0.1, value=70.0, key="w_weight")
                h = st.number_input("Height (m)", min_value=0.5, step=0.01, value=1.75, key="w_height")
            else:
                w_lbs = st.number_input("Weight (lbs)", min_value=2.0, step=0.1, value=154.0, key="w_weight_lbs")
                ft = st.number_input("Height - Feet", min_value=1, step=1, value=5, key="w_feet")
                inc = st.number_input("Height - Inches", min_value=0, max_value=11, step=1, value=9, key="w_inches")
                w = lbs_to_kg(w_lbs)
                h = feet_inches_to_m(ft, inc)
            
            bmi = calculate_bmi(w, h)
            category = get_category(bmi)
            st.info(f"Your BMI: {bmi:.1f} → Category: **{category}**")
        
        goal = st.radio("What's your main goal?", ["lose", "build", "maintain"])
        
        generate_btn = st.button("Generate Workout Plan", type="primary", use_container_width=True)
    
    if generate_btn:
        with col2:
            st.markdown(f"""
            <div class="bmi-card">
                <h3>Your Plan</h3>
                <p><strong>BMI Category:</strong> {category}</p>
                <p><strong>Goal:</strong> {goal}</p>
            </div>
            """, unsafe_allow_html=True)
            
            plan = get_workout_plan(category, goal)
            
            st.markdown("### 📋 Recommended Approach")
            for item in plan:
                st.markdown(f"- {item}")
            
            st.markdown("### 📅 Sample Weekly Schedule")
            if goal == "lose":
                st.code("""
Mon: Full-body strength    Tue: Cardio (30 min)
Wed: Rest/walk             Thu: Full-body strength
Fri: Cardio (30 min)       Sat: Active recovery (walk/stretch)
Sun: Rest
""")
            elif goal == "build":
                st.code("""
Mon: Upper body strength   Tue: Lower body strength
Wed: Rest                  Thu: Push (chest/shoulders/triceps)
Fri: Pull (back/biceps)    Sat: Legs
Sun: Rest
""")
            else:
                st.code("""
Mon: Strength              Tue: Cardio
Wed: Mobility/yoga         Thu: Strength
Fri: Cardio                Sat: Fun activity/sport
Sun: Rest
""")
            
            st.caption("This is a general template - adjust volume/intensity to your fitness level.")

# ============================================================================
# History
# ============================================================================

elif app_mode == "History":
    st.header("📜 BMI History")
    
    history = load_history()
    
    if not history:
        st.info("No history yet! Log your first BMI result to start tracking.")
    else:
        names = list(history.keys())
        selected_name = st.selectbox("Select a person to view history:", ["Show All"] + names)
        
        if selected_name == "Show All":
            for name in names:
                st.markdown(f"### {name}")
                for entry in history[name]:
                    st.text(entry)
                st.divider()
        else:
            st.markdown(f"### {selected_name}")
            for entry in history[selected_name]:
                st.text(entry)
            
            if st.button("Clear this person's history?"):
                st.warning("This feature would require file manipulation. Check back for updates!")

# ============================================================================
# Progress Trend
# ============================================================================

elif app_mode == "Progress Trend":
    st.header("📈 BMI Progress Trend")
    
    history = load_history()
    
    if not history:
        st.info("No history yet! Log a few BMI results to see a trend.")
    else:
        names = list(history.keys())
        selected_name = st.selectbox("Select a person:", names)
        
        entries = history[selected_name]
        data = []
        for entry in entries:
            try:
                parts = entry.split("|")
                date_part = parts[0].strip()
                bmi_part = [p for p in parts if "BMI:" in p]
                if bmi_part:
                    bmi_str = bmi_part[0].split(":")[1].strip().split("|")[0].strip()
                    bmi_val = float(bmi_str)
                    data.append({"Date": date_part, "BMI": bmi_val})
            except:
                continue
        
        if len(data) < 2:
            st.info("Only one logged entry so far - log another to see a trend!")
        else:
            df = pd.DataFrame(data)
            df = df.sort_values("Date")
            
            st.line_chart(df.set_index("Date"))
            
            st.markdown("### 📊 Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("First BMI", f"{df['BMI'].iloc[0]:.1f}")
            with col2:
                st.metric("Current BMI", f"{df['BMI'].iloc[-1]:.1f}")
            with col3:
                st.metric("Change", f"{df['BMI'].iloc[-1] - df['BMI'].iloc[0]:+.1f}")
            with col4:
                st.metric("Entries", len(data))
            
            # Display data table
            st.dataframe(df, hide_index=True, use_container_width=True)

# ============================================================================
# Footer
# ============================================================================

st.sidebar.divider()
st.sidebar.markdown("""
⚠️ **Disclaimer**  
BMI is a simple screening tool, not a full health diagnosis.  
It doesn't account for muscle mass, bone density, or body composition.  

This program was made by a student.  
Please don't treat it as medical advice - check with a real doctor or nutritionist.
""")

st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ using Streamlit")