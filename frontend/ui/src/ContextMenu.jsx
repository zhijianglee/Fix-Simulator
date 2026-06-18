function ContextMenu({ visible, x, y, items, onSelect }) {
  if (!visible) {
    return null;
  }

  return (
    <div className="context-menu" style={{ left: x, top: y, position: 'absolute', zIndex: 1000 }}>
      <ul>
        {items.map((item) => (
          <li key={item.key} onClick={() => onSelect(item.key)}>
            {item.label}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ContextMenu;
