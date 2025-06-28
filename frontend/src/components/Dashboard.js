import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../config/axios';

function Dashboard() {
  const [groups, setGroups] = useState([]);
  const [newGroupName, setNewGroupName] = useState('');
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      const response = await api.get('/groups');
      setGroups(response.data);
    } catch (error) {
      console.error('Failed to fetch groups:', error);
    }
  };

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    if (!newGroupName.trim()) return;

    try {
      await api.post('/groups', { name: newGroupName });
      setNewGroupName('');
      fetchGroups();
    } catch (error) {
      console.error('Failed to create group:', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <header>
        <h1>Welcome, {user?.username}</h1>
        <button onClick={handleLogout}>Logout</button>
      </header>

      <section className="create-group">
        <h2>Create New Group</h2>
        <form onSubmit={handleCreateGroup}>
          <input
            type="text"
            value={newGroupName}
            onChange={(e) => setNewGroupName(e.target.value)}
            placeholder="Group Name"
          />
          <button type="submit">Create Group</button>
        </form>
      </section>

      <section className="groups-list">
        <h2>Your Groups</h2>
        {groups.length === 0 ? (
          <p>No groups yet. Create one to get started!</p>
        ) : (
          <ul>
            {groups.map((group) => (
              <li key={group.id}>
                <div className="group-card" onClick={() => navigate(`/groups/${group.id}`)}>
                  <h3>{group.name}</h3>
                  <p>{group.description}</p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

export default Dashboard;
