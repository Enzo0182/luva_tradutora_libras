🧤 Luva Tradutora de Libras - Sistemas Embarcados & IA

Este projeto consiste no desenvolvimento de uma luva inteligente capaz de capturar os movimentos e a angulação dos dedos para traduzir a Língua Brasileira de Sinais (Libras) em texto ou voz. Diferente de soluções baseadas em câmeras, este sistema utiliza sensores físicos para garantir maior precisão de movimento e portabilidade.
🚀 Sobre o Projeto

Desenvolvido como projeto acadêmico no curso de Análise e Desenvolvimento de Sistemas (ADS), o sistema foca na coleta de dados biométricos das mãos através de sensores integrados ao hardware da luva. O processamento desses dados permite identificar padrões de sinais de forma rápida e eficiente.
✨ Funcionalidades

    Captura de Movimento: Leitura em tempo real da curvatura dos dedos e posição da mão.

    Processamento de Sinais: Algoritmos que interpretam os dados analógicos/digitais dos sensores.

    Tradução Direta: Conversão dos padrões capturados para caracteres ou áudio.

    Acessibilidade Móvel: Design focado em ser usado em qualquer ambiente, sem dependência de iluminação externa ou câmeras.

🛠️ Tecnologias Utilizadas

O projeto integra hardware e software para criar uma solução completa:

    Microcontrolador: [Arduino / ESP32 / Raspberry Pi Pico] (Ajuste conforme o que estiverem usando)

    Sensores: Sensores de Flexão (Flex Sensors), Acelerômetros e Giroscópios (MPU6050).

    Linguagem de Processamento: Python / [C++]

    Comunicação: Serial / Bluetooth / Wi-Fi.

🏗️ Como o Sistema Funciona

    Coleta: Os sensores de flexão detectam quais dedos estão dobrados e em qual intensidade.

    Orientação: O acelerômetro identifica a inclinação e a rotação do pulso.

    Processamento: Os dados são enviados ao sistema (via Python ou embarcado) que compara os valores com uma base de dados de sinais cadastrados.

    Saída: O sinal correspondente é exibido em uma interface ou reproduzido sonoramente.

📦 Instalação e Uso

    Configuração do Hardware:

        Conecte a luva via USB ou Bluetooth ao computador.

        Certifique-se de que os drivers do microcontrolador estão instalados.

    Execução do Software:
    git clone https://github.com/Enzo0182/luva_tradutora_libras.git
    cd luva_tradutora_libras
    python main.py

👥 Equipe

Este projeto é fruto do trabalho colaborativo de um grupo de 3 alunos da FAMETRO:

    ![Enzo Souza](https://github.com/Enzo0182)
    ![Eliane Braga](https://github.com/elianebfrota)
    ![Ryan Guedes](https://github.com/ryanguedis)
    

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

    Nota: Este projeto é um protótipo em desenvolvimento para fins acadêmicos.
