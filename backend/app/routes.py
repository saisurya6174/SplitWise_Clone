from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, Group, GroupMembership, Expense, ExpenseSplit, User, Settlement
from sqlalchemy import or_

bp = Blueprint('main', __name__)

@bp.route('/groups', methods=['POST'])
@jwt_required()
def create_group():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    name = data.get('name')
    description = data.get('description', '')
    
    if not name:
        return jsonify({"error": "Group name is required"}), 400
    
    new_group = Group(name=name, description=description)
    db.session.add(new_group)
    db.session.flush()  # To get the new group's ID
    
    # Add creator as the first group member
    membership = GroupMembership(user_id=current_user_id, group_id=new_group.id)
    db.session.add(membership)
    
    try:
        db.session.commit()
        return jsonify({
            "id": new_group.id,
            "name": new_group.name,
            "description": new_group.description
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/groups/<int:group_id>/expenses', methods=['POST'])
@jwt_required()
def add_expense(group_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    description = data.get('description')
    amount = data.get('amount')
    splits = data.get('splits', [])
    
    if not description or not amount or not splits:
        return jsonify({"error": "Missing required expense details"}), 400
    
    # Verify group membership
    membership = GroupMembership.query.filter_by(
        user_id=current_user_id, 
        group_id=group_id
    ).first()
    
    if not membership:
        return jsonify({"error": "Not a member of this group"}), 403
    
    # Create expense
    new_expense = Expense(
        description=description, 
        amount=amount, 
        payer_id=current_user_id, 
        group_id=group_id
    )
    db.session.add(new_expense)
    db.session.flush()
    
    # Create expense splits
    total_split_amount = 0
    for split in splits:
        user_id = split.get('user_id')
        split_amount = split.get('amount')
        
        expense_split = ExpenseSplit(
            expense_id=new_expense.id, 
            user_id=user_id, 
            amount=split_amount
        )
        db.session.add(expense_split)
        total_split_amount += split_amount
    
    # Validate total split matches expense amount
    if abs(total_split_amount - amount) > 0.01:
        db.session.rollback()
        return jsonify({"error": "Split amounts do not match total expense"}), 400
    
    try:
        db.session.commit()
        return jsonify({
            "id": new_expense.id,
            "description": new_expense.description,
            "amount": new_expense.amount
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/groups/<int:group_id>/settle', methods=['POST'])
@jwt_required()
def settle_expenses(group_id):
    current_user_id = get_jwt_identity()
    
    # Find all unsettled expense splits for this group and user
    unsettled_splits = ExpenseSplit.query.join(Expense).filter(
        Expense.group_id == group_id,
        ExpenseSplit.user_id != current_user_id,
        ExpenseSplit.is_settled == False
    ).all()
    
    settlements = []
    
    for split in unsettled_splits:
        # Create settlement record
        settlement = Settlement(
            from_user_id=current_user_id,
            to_user_id=split.user_id,
            amount=split.amount,
            group_id=group_id
        )
        db.session.add(settlement)
        
        # Mark split as settled
        split.is_settled = True
        
        settlements.append({
            "to_user_id": split.user_id,
            "amount": split.amount
        })
    
    try:
        db.session.commit()
        return jsonify({"settlements": settlements}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/groups', methods=['GET'])
@jwt_required()
def get_user_groups():
    current_user_id = get_jwt_identity()
    
    # Find all groups the user is a member of
    memberships = GroupMembership.query.filter_by(user_id=current_user_id).all()
    group_ids = [membership.group_id for membership in memberships]
    
    groups = Group.query.filter(Group.id.in_(group_ids)).all()
    
    return jsonify([{
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "created_at": group.created_at.isoformat()
    } for group in groups]), 200
