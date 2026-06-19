Esta pasta descreve como usar os worktrees criados para isolar cenários de experimento.

Branches criadas

- `topologia_ref`
- `calibrar_constantes`

Worktrees (diretórios criados)

- ../dissertacao_code_topologia_ref  (branch `topologia_ref`)
- ../calibrar_constantes            (branch `calibrar_constantes`)

Comandos úteis

- Entrar no worktree:

```
cd ../dissertacao_code_topologia_ref
```

- Ver estado git no worktree:

```
git status
```

- Comitar mudanças no worktree:

```
git add <arquivos>
git commit -m "Mensagem"
```

- Voltar ao repositório principal:

```
cd /home/nilo/Documents/dissertacao_code
```

Remoção de um worktree

```
git worktree remove ../calibrar_constantes
git branch -D calibrar_constantes
```

Boas práticas para isolamento

- Cada cenário tem sua própria branch e worktree; faça commits apenas na branch correspondente.
- Evite usar caminhos absolutos que escrevam em diretórios de outro worktree.
- Arquivos gerados (logs, outputs) preferencialmente devem ficar fora do repositório ou serem adicionados ao `.gitignore`.

Se quiser, posso adicionar entradas ao `.gitignore` para os directórios de saída de cada cenário e commitar isso automaticamente.
