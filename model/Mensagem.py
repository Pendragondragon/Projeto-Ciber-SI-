from datetime import datetime

class Mensagem:
    def __init__(self, id, titulo, texto, dataDeCriacao=None):
        self.id = id
        self.titulo = titulo
        self.texto = texto
        self.dataDeCriacao = dataDeCriacao if dataDeCriacao else datetime.now()

    def __str__(self):
        return f"Mensagem(id={self.id}, titulo='{self.titulo}', dataDeCriacao='{self.dataDeCriacao}')"