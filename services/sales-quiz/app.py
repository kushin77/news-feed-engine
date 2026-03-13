# Sales Quiz - Adaptive Product Recommendation Engine
# Task: #54 — Build Adaptive Sales Quiz & Product Selector

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
import os

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL'
)
if not app.config['SQLALCHEMY_DATABASE_URI']:
    raise ValueError("DATABASE_URL environment variable is required")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise ValueError("SECRET_KEY environment variable is required")

db = SQLAlchemy(app)

# In-memory store for quiz sessions (use Redis in production)
quiz_sessions = {}


# ==================== MODELS ====================

class QuizSession(db.Model):
    __tablename__ = 'quiz_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = db.Column(db.String(36), nullable=True)
    current_question = db.Column(db.Integer, default=0)
    answers = db.Column(db.JSON, default=dict)
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed
    recommended_products = db.Column(db.JSON, default=None)
    converted_product = db.Column(db.String(50), default=None)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.String(50), unique=True, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False)  # choice, text, number
    options = db.Column(db.JSON, default=list)  # List of choices for choice type
    next_question_branch = db.Column(db.JSON, default=dict)  # Branching logic
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    tier = db.Column(db.String(50), nullable=False)  # Free, Starter, Pro, Agency, White-label
    price = db.Column(db.Float, nullable=False)
    features = db.Column(db.JSON, default=list)
    target_segments = db.Column(db.JSON, default=list)  # Matching segments
    is_active = db.Column(db.Boolean, default=True)


class QuizAnalytics(db.Model):
    __tablename__ = 'quiz_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # started, answered, completed, converted
    question_id = db.Column(db.String(50), nullable=True)
    data = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


# ==================== QUESTION DEFINITIONS ====================

def get_quiz_flow():
    """Returns the complete quiz flow with questions and branching logic."""
    return {
        "questions": [
            {
                "question_id": "q1_platform_usage",
                "question_text": "How are you primarily using our platform?",
                "question_type": "choice",
                "options": [
                    {"value": "content_creation", "label": "Content Creation", "percentage": 25},
                    {"value": "analytics", "label": "Analytics & Insights", "percentage": 30},
                    {"value": "monetization", "label": "Monetization", "percentage": 45}
                ],
                "next_question_branch": {
                    "content_creation": "q2a_posting_frequency",
                    "analytics": "q2b_goals",
                    "monetization": "q2c_audience_size"
                }
            },
            # Branch A: Content Creation
            {
                "question_id": "q2a_posting_frequency",
                "question_text": "How often do you post content?",
                "question_type": "choice",
                "options": [
                    {"value": "less_than_1", "label": "Less than 1 post/week"},
                    {"value": "1_3", "label": "1-3 posts/week"},
                    {"value": "3_7", "label": "3-7 posts/week"},
                    {"value": "more_than_7", "label": "More than 7 posts/week"}
                ],
                "next_question_branch": {
                    "default": "q3_team_size"
                }
            },
            # Branch B: Analytics
            {
                "question_id": "q2b_goals",
                "question_text": "What's your main analytics goal?",
                "question_type": "choice",
                "options": [
                    {"value": "track_performance", "label": "Track Performance"},
                    {"value": "understand_audience", "label": "Understand My Audience"},
                    {"value": "optimize_content", "label": "Optimize Content Strategy"}
                ],
                "next_question_branch": {
                    "default": "q3_team_size"
                }
            },
            # Branch C: Monetization
            {
                "question_id": "q2c_audience_size",
                "question_text": "What's your current audience size?",
                "question_type": "choice",
                "options": [
                    {"value": "under_1k", "label": "Under 1K followers"},
                    {"value": "1k_10k", "label": "1K-10K followers"},
                    {"value": "10k_100k", "label": "10K-100K followers"},
                    {"value": "over_100k", "label": "Over 100K followers"}
                ],
                "next_question_branch": {
                    "default": "q3_budget"
                }
            },
            # Common questions
            {
                "question_id": "q3_team_size",
                "question_text": "Are you working solo or with a team?",
                "question_type": "choice",
                "options": [
                    {"value": "solo", "label": "Solo (just me)"},
                    {"value": "small_team", "label": "Small team (2-5)"},
                    {"value": "agency", "label": "Agency (5+)"}
                ],
                "next_question_branch": {
                    "default": "q4_budget"
                }
            },
            {
                "question_id": "q4_budget",
                "question_text": "What's your monthly budget for tools/platforms?",
                "question_type": "choice",
                "options": [
                    {"value": "0_50", "label": "$0-50"},
                    {"value": "50_200", "label": "$50-200"},
                    {"value": "200_500", "label": "$200-500"},
                    {"value": "over_500", "label": "$500+"}
                ],
                "next_question_branch": {
                    "default": "q5_primary_goal"
                }
            },
            {
                "question_id": "q5_primary_goal",
                "question_text": "What's your primary goal?",
                "question_type": "choice",
                "options": [
                    {"value": "growth", "label": "Grow Followers"},
                    {"value": "revenue", "label": "Increase Revenue"},
                    {"value": "efficiency", "label": "Workflow Efficiency"},
                    {"value": "engagement", "label": "Better Engagement"}
                ],
                "next_question_branch": {
                    "default": "complete"
                }
            }
        ],
        "question_order": [
            "q1_platform_usage",
            "q2a_posting_frequency",  # or q2b_goals or q2c_audience_size
            "q3_team_size",
            "q4_budget",
            "q5_primary_goal"
        ]
    }


def get_next_question(current_question_id, answer_value):
    """Determine the next question based on current answer."""
    quiz_flow = get_quiz_flow()
    
    for question in quiz_flow["questions"]:
        if question["question_id"] == current_question_id:
            branch = question.get("next_question_branch", {})
            next_q = branch.get(answer_value, branch.get("default"))
            return next_q
    return None


def get_question_by_id(question_id):
    """Get a question by its ID."""
    quiz_flow = get_quiz_flow()
    for question in quiz_flow["questions"]:
        if question["question_id"] == question_id:
            return question
    return None


# ==================== RECOMMENDATION ENGINE ====================

def calculate_product_recommendations(answers):
    """
    Calculate product recommendations based on quiz answers.
    Returns top 3 recommended products with confidence scores.
    """
    # Scoring model based on answers
    scores = {}
    
    # Get platform usage
    platform_usage = answers.get("q1_platform_usage", "")
    
    # Get audience size (if monetization path)
    audience_size = answers.get("q2c_audience_size", "")
    
    # Get budget
    budget = answers.get("q4_budget", "")
    
    # Get team size
    team_size = answers.get("q3_team_size", "")
    
    # Get primary goal
    primary_goal = answers.get("q5_primary_goal", "")
    
    # Define product recommendations based on segments
    product_scores = {
        "free": {
            "base_score": 50,
            "segments": {
                "under_1k": 20,
                "1k_10k": 10,
                "0_50": 30,
                "solo": 10
            }
        },
        "starter": {
            "base_score": 60,
            "segments": {
                "under_1k": 25,
                "1k_10k": 30,
                "1_3": 15,
                "3_7": 10,
                "50_200": 25,
                "solo": 15,
                "small_team": 10
            }
        },
        "pro": {
            "base_score": 70,
            "segments": {
                "1k_10k": 25,
                "10k_100k": 30,
                "3_7": 20,
                "more_than_7": 25,
                "50_200": 20,
                "200_500": 30,
                "small_team": 20,
                "agency": 15,
                "growth": 15,
                "revenue": 20,
                "engagement": 15
            }
        },
        "agency": {
            "base_score": 65,
            "segments": {
                "10k_100k": 20,
                "over_100k": 30,
                "more_than_7": 25,
                "200_500": 25,
                "over_500": 30,
                "agency": 30,
                "small_team": 15,
                "revenue": 25,
                "efficiency": 20
            }
        },
        "white-label": {
            "base_score": 50,
            "segments": {
                "over_100k": 25,
                "over_500": 30,
                "agency": 20,
                "revenue": 25
            }
        }
    }
    
    # Calculate scores for each product
    for product, scoring in product_scores.items():
        score = scoring["base_score"]
        
        # Add segment-based scores
        for answer_key, answer_value in answers.items():
            if answer_value in scoring["segments"]:
                score += scoring["segments"][answer_value]
        
        scores[product] = min(score, 100)  # Cap at 100
    
    # Sort by score and get top 3
    sorted_products = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Generate recommendations
    recommendations = []
    product_tiers = {
        "free": {"name": "Free", "price": 0, "confidence": 0.5},
        "starter": {"name": "Starter", "price": 25, "confidence": 0.65},
        "pro": {"name": "Pro", "price": 100, "confidence": 0.80},
        "agency": {"name": "Agency", "price": 500, "confidence": 0.75},
        "white-label": {"name": "White-label", "price": 2000, "confidence": 0.70}
    }
    
    for product, score in sorted_products:
        tier_info = product_tiers.get(product, {})
        confidence = score / 100
        
        # Generate reasoning based on answers
        reasoning = generate_reasoning(product, answers)
        
        recommendations.append({
            "product": tier_info.get("name", product.title()),
            "tier": product,
            "price": tier_info.get("price", 0),
            "confidence": round(confidence, 2),
            "reasoning": reasoning,
            "estimated_roi": calculate_roi(product, answers)
        })
    
    return recommendations


def generate_reasoning(product, answers):
    """Generate personalized reasoning for the recommendation."""
    reasons = []
    
    audience = answers.get("q2c_audience_size", "")
    budget = answers.get("q4_budget", "")
    goal = answers.get("q5_primary_goal", "")
    platform = answers.get("q1_platform_usage", "")
    
    if product == "free":
        if budget in ["0_50", ""]:
            reasons.append("Fits within your current budget")
        if audience in ["under_1k", ""]:
            reasons.append("Perfect for your current audience size")
            
    elif product == "starter":
        if audience in ["1k_10k", "under_1k"]:
            reasons.append("Ideal for growing creators like yourself")
        if budget in ["50_200"]:
            reasons.append("Best value for your budget range")
        if platform == "analytics":
            reasons.append("Unlock advanced analytics features")
            
    elif product == "pro":
        if audience in ["10k_100k", "1k_10k"]:
            reasons.append("Designed for serious creators with your audience")
        if budget in ["200_500", "50_200"]:
            reasons.append("Maximum features for your investment")
        if goal == "revenue":
            reasons.append("Includes all monetization tools")
        if goal == "engagement":
            reasons.append("Advanced engagement tracking included")
            
    elif product == "agency":
        if audience in ["over_100k", "10k_100k"]:
            reasons.append("Built for influencers at your scale")
        if budget in ["over_500", "200_500"]:
            reasons.append("Enterprise features for your budget")
        if goal == "efficiency":
            reasons.append("Team collaboration features included")
            
    elif product == "white-label":
        if audience == "over_100k":
            reasons.append("Full white-label solution for your brand")
        if goal == "revenue":
            reasons.append("Maximum revenue potential with custom branding")
    
    return ". ".join(reasons) if reasons else "Recommended based on your quiz responses"


def calculate_roi(product, answers):
    """Calculate estimated ROI for the product tier."""
    roi_multipliers = {
        "free": 1.0,
        "starter": 1.5,
        "pro": 2.5,
        "agency": 3.5,
        "white-label": 5.0
    }
    
    base_roi = roi_multipliers.get(product, 1.0)
    goal = answers.get("q5_primary_goal", "")
    
    # Adjust ROI based on goal alignment
    if goal == "revenue" and product in ["pro", "agency", "white-label"]:
        base_roi *= 1.5
    elif goal == "growth" and product in ["starter", "pro"]:
        base_roi *= 1.3
    
    return round(base_roi, 1)


# ==================== API ENDPOINTS ====================

@app.route('/v1/sales-quiz/start', methods=['POST'])
def start_quiz():
    """Start a new quiz session."""
    data = request.get_json() or {}
    creator_id = data.get('creator_id')
    
    session_id = str(uuid.uuid4())
    
    # Create session in database
    session = QuizSession(
        id=session_id,
        creator_id=creator_id,
        current_question=0,
        answers={},
        status='in_progress'
    )
    db.session.add(session)
    db.session.commit()
    
    # Log analytics
    analytics = QuizAnalytics(
        session_id=session_id,
        event_type='started',
        data={"creator_id": creator_id}
    )
    db.session.add(analytics)
    db.session.commit()
    
    # Get first question
    first_question = get_question_by_id("q1_platform_usage")
    
    return jsonify({
        "session_id": session_id,
        "first_question": first_question,
        "progress": 0
    })


@app.route('/v1/sales-quiz/sessions/<session_id>/answer', methods=['POST'])
def submit_answer(session_id):
    """Submit an answer and get the next question."""
    data = request.get_json()
    question_id = data.get('question_id')
    answer = data.get('answer')
    
    # Get session
    session = QuizSession.query.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    # Update answers
    answers = session.answers or {}
    answers[question_id] = answer
    session.answers = answers
    
    # Log analytics
    analytics = QuizAnalytics(
        session_id=session_id,
        event_type='answered',
        question_id=question_id,
        data={"answer": answer}
    )
    db.session.add(analytics)
    
    # Determine next question
    next_question_id = get_next_question(question_id, answer)
    
    if next_question_id == "complete" or not next_question_id:
        # Quiz complete - generate recommendations
        session.status = 'completed'
        recommendations = calculate_product_recommendations(answers)
        session.recommended_products = recommendations
        
        # Log completion
        completion_analytics = QuizAnalytics(
            session_id=session_id,
            event_type='completed',
            data={"recommendations": recommendations}
        )
        db.session.add(completion_analytics)
        
        db.session.commit()
        
        return jsonify({
            "status": "completed",
            "recommendations": recommendations,
            "progress": 100
        })
    
    # Get next question
    next_question = get_question_by_id(next_question_id)
    
    # Calculate progress
    total_questions = 5  # Average quiz length
    progress = int((len(answers) / total_questions) * 100)
    
    db.session.commit()
    
    return jsonify({
        "next_question": next_question,
        "progress": min(progress, 95)
    })


@app.route('/v1/sales-quiz/sessions/<session_id>/recommendation', methods=['GET'])
def get_recommendation(session_id):
    """Get product recommendations for a completed quiz."""
    session = QuizSession.query.get(session_id)
    
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    if session.status != 'completed':
        return jsonify({"error": "Quiz not completed"}), 400
    
    recommendations = session.recommended_products or []
    
    # Add custom offer (e.g., limited time discount)
    custom_offer = None
    if recommendations:
        # Example: 25% off for first month
        custom_offer = {
            "type": "limited_time",
            "discount": 0.25,
            "message": f"First month 25% off {recommendations[0]['product']} (${int(recommendations[0]['price'] * 0.75)})"
        }
    
    return jsonify({
        "recommended_products": recommendations,
        "custom_offer": custom_offer
    })


@app.route('/v1/sales-quiz/sessions/<session_id>/converted', methods=['POST'])
def track_conversion(session_id):
    """Track when a user converts to a paid product."""
    data = request.get_json()
    product = data.get('product')
    trial_days = data.get('trial_days', 14)
    
    session = QuizSession.query.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    session.converted_product = product
    
    # Log conversion
    conversion_analytics = QuizAnalytics(
        session_id=session_id,
        event_type='converted',
        data={"product": product, "trial_days": trial_days}
    )
    db.session.add(conversion_analytics)
    
    db.session.commit()
    
    from datetime import datetime, timedelta
    trial_ends = datetime.utcnow() + timedelta(days=trial_days)
    
    return jsonify({
        "status": "converted",
        "product": product,
        "trial_ends": trial_ends.isoformat()
    })


@app.route('/v1/sales-quiz/analytics/completion', methods=['GET'])
def get_completion_analytics():
    """Get quiz completion analytics."""
    total_sessions = QuizSession.query.count()
    completed_sessions = QuizSession.query.filter_by(status='completed').count()
    
    completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    return jsonify({
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "completion_rate": round(completion_rate, 2)
    })


@app.route('/v1/sales-quiz/analytics/conversion', methods=['GET'])
def get_conversion_analytics():
    """Get conversion analytics."""
    completed_sessions = QuizSession.query.filter_by(status='completed').all()
    
    converted = sum(1 for s in completed_sessions if s.converted_product)
    conversion_rate = (converted / len(completed_sessions) * 100) if completed_sessions else 0
    
    # Group by product
    product_conversions = {}
    for session in completed_sessions:
        if session.converted_product:
            product = session.converted_product
            product_conversions[product] = product_conversions.get(product, 0) + 1
    
    return jsonify({
        "total_completions": len(completed_sessions),
        "total_conversions": converted,
        "conversion_rate": round(conversion_rate, 2),
        "conversions_by_product": product_conversions
    })


# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "sales-quiz"
    })


# ==================== DATABASE SETUP ====================

def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        
        # Seed default products if not exists
        if Product.query.count() == 0:
            products = [
                Product(product_id="free", name="Free Tier", tier="Free", price=0,
                       features=["1 post/day", "Basic analytics", "Community support"],
                       target_segments=["under_1k", "0_50", "solo"]),
                Product(product_id="starter", name="Starter Tier", tier="Starter", price=25,
                       features=["5 posts/day", "Advanced analytics", "A/B testing", "Email support"],
                       target_segments=["1k_10k", "50_200", "solo", "small_team"]),
                Product(product_id="pro", name="Pro Tier", tier="Pro", price=100,
                       features=["Unlimited posts", "Full analytics", "A/B testing", "Priority support", "Monetization tools"],
                       target_segments=["10k_100k", "200_500", "small_team", "agency"]),
                Product(product_id="agency", name="Agency Tier", tier="Agency", price=500,
                       features=["Multi-client", "White-label", "API access", "Dedicated support", "Custom integrations"],
                       target_segments=["over_100k", "over_500", "agency"]),
                Product(product_id="white-label", name="White-label Tier", tier="White-label", price=2000,
                       features=["Full custom branding", "Custom domain", "SLA", "Custom development"],
                       target_segments=["over_100k", "over_500", "agency"])
            ]
            db.session.bulk_save_objects(products)
            db.session.commit()
            print("Default products seeded")


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
