import React, { useState, useEffect } from 'react';
import ContextMenu from './ContextMenu';
import LegendModal from './LegendModal';
import {
  ordStatusInfo,
  ordTypeInfo,
  sideInfo,
  timeInForceInfo,
  execTransTypeInfo,
  legendColumns,
  findLegendForColumn,
} from './legends';

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
  const [selectedColumns, setSelectedColumns] = useState([]);
  const [ordersError, setOrdersError] = useState(null);
  const [activeTab, setActiveTab] = useState('send');
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, row: null });
  const [viewDetails, setViewDetails] = useState(null);
  const [statusLegendOpen, setStatusLegendOpen] = useState(false);
  const [ordTypeLegendOpen, setOrdTypeLegendOpen] = useState(false);
  const [sideLegendOpen, setSideLegendOpen] = useState(false);
  const [tifLegendOpen, setTifLegendOpen] = useState(false);
  const [execTransTypeLegendOpen, setExecTransTypeLegendOpen] = useState(false);

  // Map legend state keys to their state setters
  const legendStateSetters = {
    statusLegendOpen: setStatusLegendOpen,
    ordTypeLegendOpen: setOrdTypeLegendOpen,
    sideLegendOpen: setSideLegendOpen,
    tifLegendOpen: setTifLegendOpen,
    execTransTypeLegendOpen: setExecTransTypeLegendOpen,
  };

  const legendStates = {
    statusLegendOpen,
    ordTypeLegendOpen,
    sideLegendOpen,
    tifLegendOpen,
    execTransTypeLegendOpen,
  };

  const statusColumns = new Set(['39', 'OrdStatus', 'ORDSTATUS', 'ordstatus']);

  const ordTypeColumns = new Set(['40', 'OrdType', 'ORDTYPE', 'ordtype', 'order_type', 'ORDER_TYPE', 'Order_Type', 'OrderType']);
  const sideColumns = new Set(['54', 'Side', 'SIDE', 'side']);
  const tifColumns = new Set(['108', 'TimeInForce', 'TIMEINFORCE', 'timeinforce', 'time_in_force', 'TIME_IN_FORCE', 'Time_In_Force']);
  const execTransTypeColumns = new Set(['150', 'ExecTransType', 'EXECTRANSTYPE', 'exectranstype', 'exec_trans_type', 'EXEC_TRANS_TYPE', 'Exec_Trans_Type']);

  const renderHeaderLabel = (col) => {
    const legend = findLegendForColumn(col);
    if (legend) {
      const setter = legendStateSetters[legend.stateKey];
      return (
        <button
          type="button"
          className="status-header-button"
          onClick={() => setter(true)}
        >
          {col}
          <span className="status-info-icon" aria-label={`Open ${legend.title.toLowerCase()}`}>ℹ</span>
        </button>
      );
    }
    return col;
  };

  const getOrderStatusKey = (row) => {
    const value = row.OrdStatus ?? row.ORDSTATUS ?? row['39'] ?? row.ordstatus;
    return value != null ? String(value).trim().toUpperCase() : '';
  };

  const getRowStatusClass = (row) => {
    return ordStatusInfo[getOrderStatusKey(row)]?.className || '';
  };

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

  useEffect(() => {
    if (Array.isArray(ordersResult) && ordersResult.length > 0) {
      const cols = Object.keys(ordersResult[0]);
      setSelectedColumns((current) =>
        current.length > 0 ? current.filter((col) => cols.includes(col)) : cols
      );
    }
  }, [ordersResult]);

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

      <div className="tabs">
        <button type="button" className={activeTab === 'send' ? 'active' : ''} onClick={() => setActiveTab('send')}>
          Send Custom Message
        </button>
        <button type="button" className={activeTab === 'retrieve' ? 'active' : ''} onClick={() => setActiveTab('retrieve')}>
          Retrieve Orders
        </button>
      </div>

      {activeTab === 'send' && (
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
      )}

      {activeTab === 'retrieve' && (
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
            <div className="orders-data">
              <div className="column-selection">
                <strong>Columns to show:</strong>
                <div className="column-actions">
                  <button
                    type="button"
                    onClick={() => setSelectedColumns(Object.keys(ordersResult[0]))}
                  >
                    Select all
                  </button>
                  <button
                    type="button"
                    onClick={() => setSelectedColumns([])}
                  >
                    Deselect all
                  </button>
                </div>
                <div className="column-checkboxes">
                  {Object.keys(ordersResult[0]).map((col) => (
                    <label key={col}>
                      <input
                        type="checkbox"
                        checked={selectedColumns.includes(col)}
                        onChange={(evt) => {
                          const checked = evt.target.checked;
                          setSelectedColumns((prev) =>
                            checked ? [...prev, col] : prev.filter((value) => value !== col)
                          );
                        }}
                      />
                      {col}
                    </label>
                  ))}
                </div>
              </div>

              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      {selectedColumns.length > 0
                        ? selectedColumns.map((col) => <th key={col}>{renderHeaderLabel(col)}</th>)
                        : <th>No columns selected</th>}
                    </tr>
                  </thead>
                  <tbody>
                    {ordersResult.map((row, idx) => (
                      <tr
                        key={idx}
                        className={getRowStatusClass(row)}
                        onContextMenu={(e) => handleRowContextMenu(e, row)}
                      >
                        {selectedColumns.length > 0
                          ? selectedColumns.map((col) => (
                              <td key={col}>{row[col] != null ? String(row[col]) : ''}</td>
                            ))
                          : <td />}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <ContextMenu
                visible={contextMenu.visible}
                x={contextMenu.x}
                y={contextMenu.y}
                items={[
                  { key: 'dfd', label: 'Send DFD' },
                  { key: 'cancel', label: 'Send Cancellation' },
                  { key: 'accept', label: 'Send Accept Order' },
                  { key: 'reject', label: 'Send Reject Order' },
                  { key: 'sendfills', label: 'Send Fills' },
                  { key: 'customMessage', label: 'Send Custom Message' },
                ]}
                onSelect={handleMenuAction}
              />

              <LegendModal
                isOpen={statusLegendOpen}
                onClose={() => setStatusLegendOpen(false)}
                title="OrdStatus legend"
                description="Rows are highlighted by FIX tag 39 / OrdStatus."
                legendData={ordStatusInfo}
              />

              <LegendModal
                isOpen={ordTypeLegendOpen}
                onClose={() => setOrdTypeLegendOpen(false)}
                title="OrdType legend"
                description="FIX tag 40 / OrdType specifies the order type."
                legendData={ordTypeInfo}
              />

              <LegendModal
                isOpen={sideLegendOpen}
                onClose={() => setSideLegendOpen(false)}
                title="Side legend"
                description="FIX tag 54 / Side specifies whether this is a buy or sell order."
                legendData={sideInfo}
              />

              <LegendModal
                isOpen={tifLegendOpen}
                onClose={() => setTifLegendOpen(false)}
                title="TimeInForce legend"
                description="FIX tag 108 / TimeInForce specifies the validity period of the order."
                legendData={timeInForceInfo}
              />

              <LegendModal
                isOpen={execTransTypeLegendOpen}
                onClose={() => setExecTransTypeLegendOpen(false)}
                title="ExecTransType legend"
                description="FIX tag 20 / ExecTransType specifies the type of execution transaction."
                legendData={execTransTypeInfo}
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
      )}
    </div>
  );
}

export default App;