import React, { useState, useEffect } from 'react';
import ContextMenu from './ContextMenu';

function App() {
  const [messageData, setMessageData] = useState({
    '11': '',
    '49': 'OMS_OCBC_01',
    '56': 'LZJSIM',
  });
  const [customJson, setCustomJson] = useState('');
  const [messageResult, setMessageResult] = useState(null);
  const [clientCompId, setClientCompId] = useState('OMS_OCBC_01');
  const [ordersResult, setOrdersResult] = useState(null);
  const [ordersError, setOrdersError] = useState(null);
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, row: null });
  const [viewDetails, setViewDetails] = useState(null);

  const handleSendMessage = async (event) => {
    event.preventDefault();
    let payload = { ...messageData };

    if (customJson.trim()) {
      try {
        const parsed = JSON.parse(customJson);
        payload = { ...payload, ...parsed };
      } catch (error) {
        setMessageResult({ error: 'Invalid JSON in custom message' });
        return;
      }
    }

    try {
      const response = await fetch('/send_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      setMessageResult(data);
    } catch (error) {
      setMessageResult({ error: error.message });
    }
  };

  const handleRetrieveOrders = async (event) => {
    event.preventDefault();
    setOrdersResult(null);
    setOrdersError(null);

    try {
      const response = await fetch(`/retrieve_orders_by_client_comp_id/${encodeURIComponent(clientCompId)}`);
      const data = await response.json();
      if (!response.ok) {
        setOrdersError(data);
        return;
      }
      setOrdersResult(data);
    } catch (error) {
      setOrdersError({ error: error.message });
    }
  };

  const handleRowContextMenu = (event, row) => {
    event.preventDefault();
    setContextMenu({ visible: true, x: event.pageX, y: event.pageY, row });
  };

  const closeContextMenu = () => setContextMenu({ visible: false, x: 0, y: 0, row: null });

  const handleMenuAction = async (action) => {
    const row = contextMenu.row;
    if (!row) return closeContextMenu();

    if (action === 'view') {
      setViewDetails(row);
    } else if (action === 'copy') {
      try {
        await navigator.clipboard.writeText(JSON.stringify(row, null, 2));
      } catch (e) {
        console.warn('Clipboard write failed', e);
      }
    } else if (action === 'actions') {
      // placeholder for custom actions (e.g., cancel order)
      alert('Actions menu for order:\n' + JSON.stringify(row, null, 2));
    }

    closeContextMenu();
  };

  // close context menu on global click
  useEffect(() => {
    const onClick = () => closeContextMenu();
    window.addEventListener('click', onClick);
    return () => window.removeEventListener('click', onClick);
  }, []);

  return (
    <div className="page-shell">
      <header>
        <h1>FIX Simulator UI</h1>
        <p>Use the backend API to send FIX messages and retrieve simulator orders.</p>
      </header>

      <section className="panel">
        <h2>Send Custom Message</h2>
        <form onSubmit={handleSendMessage}>
          <label>
            ClOrdID (11)
            <input
              type="text"
              value={messageData['11']}
              onChange={(evt) => setMessageData({ ...messageData, '11': evt.target.value })}
              required
            />
          </label>
          <label>
            SenderCompID (49)
            <input
              type="text"
              value={messageData['49']}
              onChange={(evt) => setMessageData({ ...messageData, '49': evt.target.value })}
              required
            />
          </label>
          <label>
            TargetCompID (56)
            <input
              type="text"
              value={messageData['56']}
              onChange={(evt) => setMessageData({ ...messageData, '56': evt.target.value })}
              required
            />
          </label>
          <label>
            Custom JSON
            <textarea
              rows="6"
              value={customJson}
              onChange={(evt) => setCustomJson(evt.target.value)}
              placeholder='{"35":"D","11":"..."}'
            />
          </label>
          <button type="submit">Send Message</button>
        </form>

        {messageResult && (
          <div className={`message-box ${messageResult.error ? 'error' : 'success'}`}>
            <strong>{messageResult.error ? 'Error' : 'Result'}:</strong>
            <pre>{JSON.stringify(messageResult, null, 2)}</pre>
          </div>
        )}
      </section>

      <section className="panel">
        <h2>Retrieve Orders by Client Comp ID</h2>
        <form onSubmit={handleRetrieveOrders}>
          <label>
            Client Comp ID
            <input
              type="text"
              value={clientCompId}
              onChange={(evt) => setClientCompId(evt.target.value)}
              required
            />
          </label>
          <button type="submit">Retrieve Orders</button>
        </form>

        {ordersError && (
          <div className="order-box error">
            <strong>Error:</strong>
            <pre>{JSON.stringify(ordersError, null, 2)}</pre>
          </div>
        )}

        {ordersResult && Array.isArray(ordersResult) && ordersResult.length > 0 && (
          <div>
            <table>
              <thead>
                <tr>
                  {Object.keys(ordersResult[0]).map((col) => (
                    <th key={col}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {ordersResult.map((row, idx) => (
                  <tr key={idx} onContextMenu={(e) => handleRowContextMenu(e, row)}>
                    {Object.keys(ordersResult[0]).map((col) => (
                      <td key={col}>{row[col] != null ? String(row[col]) : ''}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>

            <ContextMenu
              visible={contextMenu.visible}
              x={contextMenu.x}
              y={contextMenu.y}
              items={[
                { key: 'view', label: 'View JSON' },
                { key: 'copy', label: 'Copy JSON' },
                { key: 'actions', label: 'More actions' },
              ]}
              onSelect={handleMenuAction}
            />

            {viewDetails && (
              <div className="modal" onClick={() => setViewDetails(null)}>
                <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                  <h3>Order details</h3>
                  <pre>{JSON.stringify(viewDetails, null, 2)}</pre>
                  <button onClick={() => setViewDetails(null)}>Close</button>
                </div>
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
}

export default App;