// FIX Protocol Legend Data
// Centralized configuration for all order and execution legends

export const ordStatusInfo = {
  '0': {
    title: 'New',
    description: 'Outstanding order with no fills',
    className: 'status-row-new',
  },
  '1': {
    title: 'Partially Filled',
    description: 'Order has been poster-filled, leaves quantity > 0',
    className: 'status-row-partial',
  },
  '2': {
    title: 'Filled',
    description: 'Order completely filled, leaves quantity = 0',
    className: 'status-row-filled',
  },
  '3': {
    title: 'Done for Day',
    description: 'Order is no longer active for the current trading day',
    className: 'status-row-info',
  },
  '4': {
    title: 'Canceled',
    description: 'Order has been canceled by the user',
    className: 'status-row-canceled',
  },
  '5': {
    title: 'Replaced',
    description: 'Order cancel/replace request has been completed',
    className: 'status-row-info',
  },
  '6': {
    title: 'Pending Cancel',
    description: 'Cancel request received, confirmation outstanding',
    className: 'status-row-pending',
  },
  '7': {
    title: 'Stopped',
    description: 'Order execution has been stopped',
    className: 'status-row-info',
  },
  '8': {
    title: 'Rejected',
    description: 'Order was rejected by the broker/exchange',
    className: 'status-row-rejected',
  },
  '9': {
    title: 'Suspended',
    description: 'Order is temporarily inactive',
    className: 'status-row-info',
  },
  'A': {
    title: 'Pending New',
    description: 'Order received, creation confirmation outstanding',
    className: 'status-row-pending',
  },
  'B': {
    title: 'Calculated',
    description: 'Order has been calculated, typically for algorithmic models',
    className: 'status-row-info',
  },
  'C': {
    title: 'Expired',
    description: 'Order has reached its expiration time',
    className: 'status-row-expired',
  },
  'D': {
    title: 'Accepted for Bidding',
    description: 'Order is accepted in a bidding phase',
    className: 'status-row-info',
  },
  'E': {
    title: 'Pending Replace',
    description: 'Cancel/replace request received, confirmation outstanding',
    className: 'status-row-pending',
  },
};

export const ordTypeInfo = {
  '1': {
    title: 'Market',
    description: 'Market order - execute at best available price',
  },
  '2': {
    title: 'Limit',
    description: 'Limit order - execute at specified price or better',
  },
  '3': {
    title: 'Stop',
    description: 'Stop order - execute when price reaches specified level',
  },
  '4': {
    title: 'Stop Limit',
    description: 'Stop Limit order - become limit order when stop price is reached',
  },
  '5': {
    title: 'Trailing Stop',
    description: 'Trailing Stop - stop price trails behind market price',
  },
  '6': {
    title: 'Trailing Stop Limit',
    description: 'Trailing Stop Limit - limit price trails behind market price',
  },
  '7': {
    title: 'For-and-Against (FAK)',
    description: 'For-and-Against - fill against best prices, remainder returned',
  },
  '8': {
    title: 'Immediate-or-Cancel (IOC)',
    description: 'Immediate-or-Cancel - fill what available, remainder canceled',
  },
  '9': {
    title: 'Fill-or-Kill (FOK)',
    description: 'Fill-or-Kill - execute entire order or cancel completely',
  },
  'A': {
    title: 'Good-Till-Crossing (GTX)',
    description: 'Good-Till-Crossing - remain until cross with opposite side',
  },
  'B': {
    title: 'Good-Till-Date (GTD)',
    description: 'Good-Till-Date - remain until specified expiration date',
  },
  'C': {
    title: 'At-the-Opening (OPG)',
    description: 'At-the-Opening - execute at market opening',
  },
  'D': {
    title: 'At-the-Close (ATC)',
    description: 'At-the-Close - execute at market close',
  },
  'E': {
    title: 'Limit-on-Open (LOO)',
    description: 'Limit-on-Open - limit order at opening',
  },
  'F': {
    title: 'Limit-on-Close (LOC)',
    description: 'Limit-on-Close - limit order at close',
  },
};

export const sideInfo = {
  '1': {
    title: 'Buy',
    description: 'Buy side of the order',
  },
  '2': {
    title: 'Sell',
    description: 'Sell side of the order',
  },
  '3': {
    title: 'Buy Minus',
    description: 'Buy minus (short exempt)',
  },
  '4': {
    title: 'Sell Plus',
    description: 'Sell plus (uptick)',
  },
  '5': {
    title: 'Sell Short',
    description: 'Sell short',
  },
  '6': {
    title: 'Sell Short Exempt',
    description: 'Sell short exempt',
  },
  '7': {
    title: 'Undisclosed',
    description: 'Undisclosed side',
  },
  '8': {
    title: 'Cross',
    description: 'Cross order',
  },
  '9': {
    title: 'Cross Short',
    description: 'Cross short',
  },
  'A': {
    title: 'Cross Short Exempt',
    description: 'Cross short exempt',
  },
  'B': {
    title: 'As-Defined',
    description: 'As-defined by counterparty',
  },
  'C': {
    title: 'Opposite',
    description: 'Opposite to disclosed side',
  },
};

export const timeInForceInfo = {
  '0': {
    title: 'Day (DAY)',
    description: 'Order expires at end of trading day',
  },
  '1': {
    title: 'Good Till Cancel (GTC)',
    description: 'Order remains active until canceled',
  },
  '2': {
    title: 'At the Opening (OPG)',
    description: 'Order executes at opening or is canceled',
  },
  '3': {
    title: 'Immediate or Cancel (IOC)',
    description: 'Fill immediately or cancel unfilled portion',
  },
  '4': {
    title: 'Fill or Kill (FOK)',
    description: 'Entire order must fill immediately or cancel completely',
  },
  '5': {
    title: 'Good Till Crossing (GTX)',
    description: 'Remains until crossing with opposite order or expires',
  },
  '6': {
    title: 'Good Till Date (GTD)',
    description: 'Remains until specified expiration date',
  },
  '7': {
    title: 'At the Close (ATC)',
    description: 'Order executes at close or is canceled',
  },
};

export const execTransTypeInfo = {
  '0': {
    title: 'New',
    description: 'New execution transaction',
  },
  '1': {
    title: 'Cancel',
    description: 'Execution canceled',
  },
  '2': {
    title: 'Correct',
    description: 'Execution correction',
  },
  '3': {
    title: 'Status',
    description: 'Status update only',
  },
};

// Column name mappings for legend identification
export const legendColumns = {
  status: {
    columnSet: new Set(['39', 'OrdStatus', 'ORDSTATUS', 'ordstatus']),
    info: ordStatusInfo,
    title: 'OrdStatus legend',
    description: 'Rows are highlighted by FIX tag 39 / OrdStatus.',
    stateKey: 'statusLegendOpen',
  },
  ordType: {
    columnSet: new Set(['40', 'OrdType', 'ORDTYPE', 'ordtype', 'order_type', 'ORDER_TYPE', 'Order_Type', 'OrderType']),
    info: ordTypeInfo,
    title: 'OrdType legend',
    description: 'FIX tag 40 / OrdType specifies the order type.',
    stateKey: 'ordTypeLegendOpen',
  },
  side: {
    columnSet: new Set(['54', 'Side', 'SIDE', 'side']),
    info: sideInfo,
    title: 'Side legend',
    description: 'FIX tag 54 / Side specifies whether this is a buy or sell order.',
    stateKey: 'sideLegendOpen',
  },
  timeInForce: {
    columnSet: new Set(['108', 'TimeInForce', 'TIMEINFORCE', 'timeinforce', 'time_in_force', 'TIME_IN_FORCE', 'Time_In_Force']),
    info: timeInForceInfo,
    title: 'TimeInForce legend',
    description: 'FIX tag 108 / TimeInForce specifies the validity period of the order.',
    stateKey: 'tifLegendOpen',
  },
  execTransType: {
    columnSet: new Set(['150', 'ExecTransType', 'EXECTRANSTYPE', 'exectranstype', 'exec_trans_type', 'EXEC_TRANS_TYPE', 'Exec_Trans_Type']),
    info: execTransTypeInfo,
    title: 'ExecTransType legend',
    description: 'FIX tag 150 / ExecTransType specifies the type of execution transaction.',
    stateKey: 'execTransTypeLegendOpen',
  },
};

// Helper function to find which legend applies to a column
export const findLegendForColumn = (columnName) => {
  for (const [key, legend] of Object.entries(legendColumns)) {
    if (legend.columnSet.has(columnName)) {
      return { key, ...legend };
    }
  }
  return null;
};

// Helper function to get all legend configs
export const getAllLegends = () => {
  return Object.entries(legendColumns).map(([key, legend]) => ({
    key,
    ...legend,
  }));
};
