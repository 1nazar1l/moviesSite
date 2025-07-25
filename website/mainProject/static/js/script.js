startPage = document.getElementById('start_page'); 
endPage = document.getElementById('end_page'); 

startPage.addEventListener('input', function() {
  if (startPage.value.trim() !== '') {
    startPage.classList.add('active')
  } else {
    startPage.classList.remove('active')
  }
});

endPage.addEventListener('input', function() {
  if (endPage.value.trim() !== '') {
    endPage.classList.add('active')
  } else {
    endPage.classList.remove('active')
  }
});

document.addEventListener('DOMContentLoaded', function() {
  const vpnCheckbox = document.getElementById('vpn_connected');
  
  const vpnDependentElements = [
    {
      element: document.getElementById('get_media_items_id'),
      block: document.querySelector('#get_media_items_id').closest('.input_block.checkbox_type')
    },
    {
      element: document.getElementById('start_page'),
      block: document.querySelector('#start_page').closest('.input_block.text_type')
    },
    {
      element: document.getElementById('end_page'),
      block: document.querySelector('#end_page').closest('.input_block.text_type')
    },
    {
      element: document.getElementById('get_media_items_data'),
      block: document.querySelector('#get_media_items_data').closest('.input_block.checkbox_type')
    },
    {
      element: document.getElementById('download_images'),
      block: document.querySelector('#download_images').closest('.input_block.checkbox_type')
    }
  ];

  function toggleVpnDependentElements() {
    const isVpnConnected = vpnCheckbox.checked;
    
    vpnDependentElements.forEach(item => {
      if (item.element && item.block) {
        item.element.disabled = !isVpnConnected;
        item.block.classList.toggle('disabled', !isVpnConnected);
        
        if (!isVpnConnected && item.element.type === 'checkbox' && item.element.checked) {
          item.element.checked = false;
        }
      }
    });
  }

  toggleVpnDependentElements();

  vpnCheckbox.addEventListener('change', toggleVpnDependentElements);
});