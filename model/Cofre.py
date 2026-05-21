class Cofre:
    MAX_UTILIZADORES = 3

    def __init__(
        self,
        id,
        codigo_autenticacao,
        assinatura_digital,
        tipo_de_cifra: TipoDeCifra,
        hmac_hash: HMACHash,
        assinatura_hash: AssinaturaHash,
        rsa_tamanho: RSATamanho,
        mensagem,
        metadado,
        delete_token=None,
        delete_token_expira=None
    ):
        self.id = id
        self.codigo_autenticacao = codigo_autenticacao
        self.assinatura_digital = assinatura_digital
        self.tipo_de_cifra = tipo_de_cifra
        self.hmac_hash = hmac_hash
        self.assinatura_hash = assinatura_hash
        self.rsa_tamanho = rsa_tamanho


        self.delete_token = delete_token
        self.delete_token_expira = delete_token_expira

        self.utilizadores = []
        self.mensagem = mensagem
        self.metadado = metadado

    def adicionar_utilizador(self, user):
        if len(self.utilizadores) >= Cofre.MAX_UTILIZADORES:
            raise Exception("Limite de utilizadores atingido (máx. 3).")

        if user in self.utilizadores:
            print("Utilizador já tem acesso ao cofre.")
            return

        self.utilizadores.append(user)

    def remover_utilizador(self, user):
        if user in self.utilizadores:
            self.utilizadores.remove(user)

    def __str__(self):
        return (
            f"Cofre(id={self.id}, tipo_de_cifra={self.tipo_de_cifra.name}, "
            f"hmac={self.hmac_hash.name}, assinatura={self.assinatura_hash.name}, "
            f"rsa={self.rsa_tamanho.value}, utilizadores={len(self.utilizadores)})"
        )

