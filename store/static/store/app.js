document.addEventListener('scroll',()=>{document.getElementById('topBtn').style.display=window.scrollY>200?'block':'none';});
document.getElementById('topBtn').addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));
