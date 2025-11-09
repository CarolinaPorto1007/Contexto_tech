document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('palavraInput');
    const button = document.getElementById('tentarBtn');
    const feedback = document.getElementById('feedback');
    const progressBar = document.getElementById('progress-bar');
    const tentativas = document.getElementById('tentativas');
    const reiniciarBtn = document.getElementById('reiniciarBtn');

    button.addEventListener('click', async () => {
        const palavra = input.value.trim();
        if (!palavra) return;

        const response = await fetch('/tentar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ palavra })
        });

        const data = await response.json();

        if (data.erro) {
            feedback.textContent = data.erro;
            feedback.style.color = "#ff6b6b";
            return;
        }

        const li = document.createElement('li');
        li.textContent = `${palavra} — Similaridade: ${data.similaridade}%`;
        tentativas.prepend(li);

        progressBar.style.width = `${data.similaridade}%`;

        if (data.venceu) {
            feedback.innerHTML = `🎉 Parabéns! A palavra era <b>${data.palavra_secreta}</b>!`;
            feedback.style.color = "#00ffb3";
            reiniciarBtn.classList.remove('hidden');
        } else {
            feedback.textContent = `Similaridade: ${data.similaridade}%`;
            feedback.style.color = "#00d4ff";
        }

        input.value = "";
    });

    reiniciarBtn.addEventListener('click', async () => {
        await fetch('/reiniciar', { method: 'POST' });
        tentativas.innerHTML = "";
        feedback.textContent = "Novo jogo iniciado!";
        feedback.style.color = "#00d4ff";
        progressBar.style.width = "0%";
        reiniciarBtn.classList.add('hidden');
    });
});
