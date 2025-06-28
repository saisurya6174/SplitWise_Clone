import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../config/axios';

function GroupExpenses() {
  const { groupId } = useParams();
  const [expenses, setExpenses] = useState([]);
  const [newExpense, setNewExpense] = useState({
    description: '',
    amount: '',
    splits: []
  });

  useEffect(() => {
    fetchExpenses();
  }, [groupId]);

  const fetchExpenses = async () => {
    try {
      const response = await api.get(`/groups/${groupId}/expenses`);
      setExpenses(response.data);
    } catch (error) {
      console.error('Failed to fetch expenses:', error);
    }
  };

  const handleAddExpense = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/groups/${groupId}/expenses`, newExpense);
      setNewExpense({ description: '', amount: '', splits: [] });
      fetchExpenses();
    } catch (error) {
      console.error('Failed to add expense:', error);
    }
  };

  const handleSettle = async () => {
    try {
      await api.post(`/groups/${groupId}/settle`);
      fetchExpenses();
    } catch (error) {
      console.error('Failed to settle expenses:', error);
    }
  };

  return (
    <div className="group-expenses">
      <h2>Group Expenses</h2>
      
      <form onSubmit={handleAddExpense}>
        <div>
          <label>Description</label>
          <input
            type="text"
            value={newExpense.description}
            onChange={(e) => setNewExpense({...newExpense, description: e.target.value})}
            required
          />
        </div>
        <div>
          <label>Amount</label>
          <input
            type="number"
            value={newExpense.amount}
            onChange={(e) => setNewExpense({...newExpense, amount: e.target.value})}
            required
          />
        </div>
        <button type="submit">Add Expense</button>
      </form>

      <div className="expenses-list">
        <h3>Recent Expenses</h3>
        {expenses.map((expense) => (
          <div key={expense.id} className="expense-item">
            <p>{expense.description}</p>
            <p>${expense.amount}</p>
          </div>
        ))}
      </div>

      <button onClick={handleSettle}>Settle Up</button>
    </div>
  );
}

export default GroupExpenses;
