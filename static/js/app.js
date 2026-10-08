const $=s=>document.querySelector(s);
let questions=[],current=0,score=0,answered=false;
const form=$('#registerForm'), msg=$('#registerMsg');
form.addEventListener('submit',async e=>{e.preventDefault();msg.textContent='';const alias=$('#alias').value.trim();try{const r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({alias})});const d=await r.json();if(!r.ok){msg.textContent=d.error||'No se pudo registrar.';return}startGame()}catch(err){msg.textContent='No se pudo conectar con el servidor.'}});
async function startGame(){const r=await fetch('/api/questions');const d=await r.json();questions=d.questions;current=0;score=0;$('#register').classList.add('hidden');$('#result').classList.add('hidden');$('#game').classList.remove('hidden');renderQuestion()}
function renderQuestion(){answered=false;const x=questions[current];$('#qCount').textContent=`${current+1} / 10`;$('#progressBar').style.width=`${(current+1)*10}%`;$('#difficulty').textContent=`NIVEL ${x.d} · ${x.d===1?'FUNDAMENTOS':x.d===2?'ANÁLISIS':'DESAFÍO'}`;$('#questionText').textContent=x.q;const box=$('#answers');box.innerHTML='';x.a.forEach((a,i)=>{const b=document.createElement('button');b.className='answer';b.textContent=a;b.onclick=()=>answer(i,b);box.appendChild(b)});$('#feedback').textContent='';$('#nextBtn').classList.add('hidden')}
function answer(i,btn){if(answered)return;answered=true;const x=questions[current];document.querySelectorAll('.answer').forEach(b=>b.disabled=true);if(i===x.c){score++;btn.classList.add('correct');$('#feedback').textContent='✓ Correcto. Buen trabajo, guardabosques.'}else{btn.classList.add('wrong');document.querySelectorAll('.answer')[x.c].classList.add('correct');$('#feedback').textContent='✕ No esta vez. La respuesta correcta quedó marcada.'}$('#nextBtn').classList.remove('hidden')}
$('#nextBtn').onclick=()=>{current++;if(current>=10)finish();else renderQuestion()};
async function finish(){await fetch('/api/quiz-finished',{method:'POST'});$('#game').classList.add('hidden');$('#result').classList.remove('hidden');$('#score').textContent=`${score}/10`;let title='';if(score<=4)title='Hay bosque por descubrir.';else if(score<=7)title='Buen trabajo, guardabosques.';else if(score<=9)title='Casi perfecto: conoces el territorio.';else title='10/10. El bosque no tiene secretos para ti.';$('#resultTitle').textContent=title;$('#resultText').textContent=`Respondiste correctamente ${score} de 10 preguntas. La partida mezcló preguntas de fundamentos, análisis y desafío.`}
$('#restartBtn').onclick=()=>{ $('#result').classList.add('hidden'); $('#register').classList.remove('hidden'); $('#alias').value=''; window.scrollTo({top:$('#quiz').offsetTop,behavior:'smooth'})};
const audio=$('#podcastAudio');$('#podcastPlay').onclick=()=>{if(!audio.src||audio.src.endsWith('/podcast.mp3')){audio.play().catch(()=>{});return}audio.paused?audio.play():audio.pause()};


// Verificación de medios integrados
document.addEventListener('DOMContentLoaded', () => {
  const video = document.getElementById('mainVideo');
  const fallback = document.getElementById('videoFallback');
  if (video && fallback) video.addEventListener('error', () => { fallback.style.display = 'block'; });
  const audio = document.getElementById('podcastAudio');
  const play = document.getElementById('podcastPlay');
  if (audio && play) play.addEventListener('click', async () => {
    try {
      if (audio.paused) { await audio.play(); play.textContent = '❚❚'; }
      else { audio.pause(); play.textContent = '▶'; }
    } catch(e) { console.error('No se pudo reproducir el podcast', e); }
  });
  if (audio && play) audio.addEventListener('ended', () => play.textContent = '▶');
});
