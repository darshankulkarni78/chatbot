import React, { useState } from 'react';
import './FormattedResponse.css';

function FormattedResponse({ response }) {
  const [showSQL, setShowSQL] = useState(false);

  const [explanation, sql] = response.split(/```sql|```/).map(part => part?.trim());

  const parts = explanation ? explanation.split(/\n|(?=\d+\.)/).filter(Boolean) : [];

  return (
    <div className="formatted-response">
      {parts.map((part, i) => {
        if (/^\d+\./.test(part.trim())) {
          return (
            <h4 key={i} style={{ marginTop: '1em', color: '#333' }}>
              {part.trim()}
            </h4>
          );
        }
        return (
          <p key={i} style={{ lineHeight: '1.6', color: '#555' }}>
            {part.trim()}
          </p>
        );
      })}

      {sql && (
        <>
          <button onClick={() => setShowSQL(!showSQL)} style={{ marginTop: '1em' }}>
            {showSQL ? 'Hide SQL Query' : 'Show SQL Query'}
          </button>
          {showSQL && <pre className="sql-code">{sql}</pre>}
        </>
      )}
    </div>
  );
}

export default FormattedResponse;
