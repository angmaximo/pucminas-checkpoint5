# Checkpoint #1 - Deploy de Função Serverless respondendo requisições HHTPP
  
o projeto tem o objetivo de subir uma aplicação que envia imagens para um repositório do tipo object storage, e envia e-mail confirmando a operação.  

## Provedor Utilizado  
* GCP (Cloud Run)    
  
## Como rodar localmente  
  
No diretório da aplicação, em um console linux ou CLoud Shell, rodar o comando: `python3 app.py`  
  
## Pré requisitos  
  
Flask  
google-cloud-storage    
python-dotenv  
google sdk  
  
### Passo a passo  
  
1. Clone o repositório para sua máquina: 
   
`git clone https://github.com/seu-usuario/pucminas-checkpoint1.git`    
  
2. Entre na pasta do projeto  
  
  `cd pucminas-checkpoint1`  
    
3. Instale as dependências:  
  
`pip install flask python-dotenv gunicorn`      
`apt install google-cloud-cli -y`  # Linux  

4. Acesse a URL da aplicação (enviada no Canvas)  
  
### Rodando a aplicação locamente  
  
  `python3 app.py`  


  





