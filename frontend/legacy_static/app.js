const messageForm = document.getElementById('message-form');
const retrieveForm = document.getElementById('retrieve-form');
const messageResult = document.getElementById('message-result');
const retrieveResult = document.getElementById('retrieve-result');

messageForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const payload = {
    '11': document.getElementById('clordid').value,
    '49': document.getElementById('sender_comp_id').value,
    '56': document.getElementById('target_comp_id').value,
  };

  const customText = document.getElementById('custom_message').value.trim();
  if (customText) {
    try {
      const customJson = JSON.parse(customText);
      Object.assign(payload, customJson);
    } catch (error) {
      messageResult.textContent = 'Invalid JSON in custom FIX message.';
      messageResult.className = 'result error';
      return;
    }
  }

  try {
    const response = await fetch('/send_message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const body = await response.json();
    if (!response.ok) {
      messageResult.textContent = JSON.stringify(body, null, 2);
      messageResult.className = 'result error';
      return;
    }

    messageResult.textContent = JSON.stringify(body, null, 2);
    messageResult.className = 'result success';
  } catch (error) {
    messageResult.textContent = `Request failed: ${error.message}`;
    messageResult.className = 'result error';
  }
});

retrieveForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const clientCompId = document.getElementById('client_comp_id').value.trim();
  if (!clientCompId) {
    retrieveResult.textContent = 'Client Comp ID is required.';
    retrieveResult.className = 'result error';
    return;
  }

  try {
    const response = await fetch(`/retrieve_orders_by_client_comp_id/${encodeURIComponent(clientCompId)}`);
    const body = await response.json();

    if (!response.ok) {
      retrieveResult.textContent = JSON.stringify(body, null, 2);
      retrieveResult.className = 'result error';
      return;
    }

    retrieveResult.textContent = JSON.stringify(body, null, 2);
    retrieveResult.className = 'result success';
  } catch (error) {
    retrieveResult.textContent = `Request failed: ${error.message}`;
    retrieveResult.className = 'result error';
  }
});
