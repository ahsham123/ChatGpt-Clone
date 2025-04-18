import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

function History() {
  const [sessions, setSessions] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const response = await api.get('/history');
      const messages = response.data;
      const grouped = messages.reduce((acc, msg) => {
        const sid = msg.session_id;
        if (!acc[sid]) acc[sid] = [];
        acc[sid].push(msg);
        return acc;
      }, {});
      const sessionList = Object.keys(grouped).map((sid) => {
        const msgs = grouped[sid];
        const last = msgs.reduce(
          (prev, curr) =>
            new Date(curr.timestamp) > new Date(prev.timestamp) ? curr : prev,
          msgs[0]
        );
        return { sessionId: sid, lastMessage: last.content, timestamp: last.timestamp };
      });
      sessionList.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      setSessions(sessionList);
    } catch (err) {
      console.error(err);
    }
  };

  const handleClick = (sid) => {
    navigate(`/chat/${sid}`);
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-8">
          <div className="card shadow-sm">
            <div className="card-header">
              <h5 className="mb-0">Chat History</h5>
            </div>
            {sessions.length === 0 ? (
              <div className="card-body">
                <p className="mb-0">No history available.</p>
              </div>
            ) : (
              <ul className="list-group list-group-flush">
                {sessions.map((sess) => (
                  <li
                    key={sess.sessionId}
                    className="list-group-item list-group-item-action"
                    onClick={() => handleClick(sess.sessionId)}
                  >
                    <div>
                      <strong>Session ID:</strong> {sess.sessionId}
                    </div>
                    <div>
                      <strong>Last Message:</strong> {sess.lastMessage}
                    </div>
                    <div>
                      <small>{new Date(sess.timestamp).toLocaleString()}</small>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default History;