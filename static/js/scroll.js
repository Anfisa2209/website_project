window.addEventListener('scroll', () => {
  const header = document.getElementById('header');
  const scrollY = window.scrollY;
  console.log(header)

  // Изменяем прозрачность фона header
 // header.style.background = `rgba(219, 199, 145, ${1 - scrollY / 300})`;
});