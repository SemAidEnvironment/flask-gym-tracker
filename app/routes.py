from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from .models import User, Workout, Exercise, db, PredefinedWorkout, PredefinedWorkoutExercise
import json
from datetime import datetime


main = Blueprint('main', __name__)



@main.route("/")
def home():
    users = User.query.all()
    return render_template("index.html", users=users)

@main.route("/log_workout/<int:user_id>", methods=["GET", "POST"])
def log_workout(user_id):
    user = User.query.get_or_404(user_id)

    # Load predefined workouts from the database
    predefined_workouts = PredefinedWorkout.query.all()

    # Serialize predefined workouts into JSON-compatible dictionaries
    def serialize_predefined_workout(workout):
        return {
            "id": workout.id,
            "name": workout.name,
            "exercises": [
                {
                    "name": exercise.name,
                    "sets": exercise.sets,
                    "repetitions": exercise.repetitions,
                    "weight": exercise.weight
                }
                for exercise in workout.exercises
            ]
        }

    serialized_workouts = [serialize_predefined_workout(workout) for workout in predefined_workouts]

    # Load exercises from JSON
    with open("exercises.json") as f:
        exercises = json.load(f)

    if request.method == "POST":
        # Capture workout date
        workout_date = request.form.get("workout_date")
        if not workout_date:
            workout_date = datetime.utcnow()
        else:
            workout_date = datetime.strptime(workout_date, "%Y-%m-%d")

        # Create a new workout
        workout = Workout(user_id=user.id, date=workout_date)
        db.session.add(workout)
        db.session.commit()

        # Capture exercise details
        selected_exercises = request.form.getlist("exercise_name")
        sets = request.form.getlist("sets")
        reps = request.form.getlist("reps")
        weights = request.form.getlist("weight")

        # Add exercises to the workout
        for i in range(len(selected_exercises)):
            exercise = Exercise(
                name=selected_exercises[i],
                sets=int(sets[i]),
                repetitions=int(reps[i]),
                weight=float(weights[i]),
                workout_id=workout.id
            )
            db.session.add(exercise)
        db.session.commit()

        return redirect(url_for("main.home"))

    return render_template(
        "log_workout.html",
        user=user,
        exercises=exercises,
        predefined_workouts=serialized_workouts
    )


@main.route("/user/<int:user_id>")
def user_page(user_id):
    user = User.query.get_or_404(user_id)

    # Fetch workouts and exercises for the user
    workouts = Workout.query.filter_by(user_id=user.id).all()
    exercises = set(exercise.name for workout in workouts for exercise in workout.exercises)

    # Generate calendar events
    calendar_dates = [
        {
            "title": "Workout",
            "start": workout.date.strftime('%Y-%m-%d'),
            "url": url_for('main.workout_details', user_id=user.id, workout_id=workout.id)
        }
        for workout in workouts
    ]

    return render_template(
        "user_page.html",
        user=user,
        workouts=workouts,
        exercises=exercises,
        calendar_dates=calendar_dates
    )




@main.route("/user/<int:user_id>/exercise/<string:exercise_name>")
def exercise_details(user_id, exercise_name):
    user = User.query.get_or_404(user_id)

    # Get all performances of the selected exercise
    performances = Exercise.query.join(Workout).filter(
        Workout.user_id == user.id,
        Exercise.name == exercise_name
    ).order_by(Workout.date).all()

    # Prepare data for the graph
    graph_data = [(performance.workout.date.strftime('%Y-%m-%d'), performance.weight) for performance in performances]

    return render_template(
        "exercise_details.html",
        user=user,
        exercise_name=exercise_name,
        performances=performances,
        graph_data=graph_data
    )

@main.route("/workouts", methods=["GET", "POST"])
def workouts():
    # Load predefined workouts from the database
    predefined_workouts = PredefinedWorkout.query.all()

    # Load exercises from JSON
    with open("exercises.json") as f:
        predefined_exercises = json.load(f)

    # Handle POST request: Add a new predefined workout
    if request.method == "POST":
        name = request.form.get("workout_name")
        exercises = request.form.getlist("exercise_name")
        sets = request.form.getlist("sets")
        reps = request.form.getlist("reps")
        weights = request.form.getlist("weight")

        # Create a new predefined workout entry
        new_workout = PredefinedWorkout(name=name)
        db.session.add(new_workout)
        db.session.commit()

        # Add exercises to the predefined workout
        for i in range(len(exercises)):
            workout_exercise = PredefinedWorkoutExercise(
                name=exercises[i],
                sets=int(sets[i]),
                repetitions=int(reps[i]),
                weight=float(weights[i]),
                workout_id=new_workout.id
            )
            db.session.add(workout_exercise)
        db.session.commit()

        return redirect(url_for("main.workouts"))

    return render_template("workouts.html", predefined_workouts=predefined_workouts,
        predefined_exercises=predefined_exercises
)


@main.route("/workout_details/<int:user_id>/<int:workout_id>")
def workout_details(user_id, workout_id):
    user = User.query.get_or_404(user_id)
    workout = Workout.query.get_or_404(workout_id)
    exercises = Exercise.query.filter_by(workout_id=workout.id).all()

    return render_template(
        "workout_details.html",
        user=user,
        workout=workout,
        exercises=exercises
    )

@main.route("/api/get_last_exercise/<int:user_id>/<string:exercise_name>")
def get_last_exercise(user_id, exercise_name):
    # Fetch the most recent logged exercise for the given user and exercise name
    last_exercise = (
        Exercise.query.join(Workout)
        .filter(Workout.user_id == user_id, Exercise.name == exercise_name)
        .order_by(Workout.date.desc(), Exercise.id.desc())  # Fetch the latest
        .first()
    )

    if last_exercise:
        # Return the most recent exercise data as JSON
        return jsonify({
            "sets": last_exercise.sets,
            "reps": last_exercise.repetitions,
            "weight": last_exercise.weight,
        })
    else:
        # Return default empty values if no data exists
        return jsonify({
            "sets": 0,
            "reps": 0,
            "weight": 0,
        })
