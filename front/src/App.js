import React, { useState} from 'react';
import './App.css';
import FormattedResponse from './FormattedResponse';
import { v4 as uuidv4 } from 'uuid';

function App() {
  const [sessionId] = useState(uuidv4());
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [tableData, setTableData] = useState([]);
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, session_id: sessionId }),
      });

      const data = await res.json();
      setResponse(data.response || 'No response from backend');
      setTableData(data.table || []);
      setQuestion('');
    } catch (err) {
      setResponse('Error connecting to backend.');
      setTableData([]);
    }
    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  };

  return (
    <div className="App">
      <h1>Ask Your Business Data</h1>

      <textarea
        rows="4"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your question... (Press Enter to send, Shift+Enter for new line)"
      />
      <br />

      <button onClick={askQuestion} disabled={loading}>
        {loading ? 'Thinking...' : 'Ask'}
      </button>

      <div className="response">
        <h3>Answer:</h3>
        <FormattedResponse response={response} />

        {tableData.length > 0 && (
          <div className="table-container">
            <h4>Data Preview:</h4>
            <table>
              <thead>
                <tr>
                  {Object.keys(tableData[0]).map((key, idx) => (
                    <th key={idx}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tableData.map((row, i) => (
                  <tr key={i}>
                    {Object.values(row).map((val, j) => (
                      <td key={j}>{val}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
