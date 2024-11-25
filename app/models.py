from . import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    workouts = db.relationship('Workout', backref='user', lazy=True)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False,index=True)
    exercises = db.relationship('Exercise', backref='workout', lazy=True)

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    repetitions = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False,index=True)

class PredefinedWorkout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    exercises = db.relationship('PredefinedWorkoutExercise', backref='workout', lazy=True)

class PredefinedWorkoutExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    repetitions = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('predefined_workout.id'), nullable=False)

