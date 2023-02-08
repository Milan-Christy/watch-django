const btn = document.getElementById('btn');

btn.addEventListener('click', () => {
  const form = document.getElementById('form');

  if (form.style.display === 'block') {
    // 👇️ this SHOWS the form
    form.style.display = 'none';
  } else {
    // 👇️ this HIDES the form
    form.style.display = 'block';
  }
});


const checkoutBtn = document.getElementById('checkout-btn');

checkoutBtn.addEventListener('click', () => {
    if ($('input[type=radio]:checked').length== 0){
      swal("Alert","Address is mandatory","error");
      return false;
    }
    else{
      document.getElementById("addressForm").submit();
      return true;
    }
});