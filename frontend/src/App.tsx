import { FormEvent, ReactNode, useEffect, useMemo, useState } from "react";
import { api } from "./api";
import { Cliente, DashboardResumo, Material, Orcamento, Retalho } from "./types";

type Aba = "dashboard" | "clientes" | "materiais" | "retalhos" | "orcamentos";

const tiposMaterial = ["mdf", "compensado", "madeira", "fita_borda", "ferragem", "insumo", "servico", "outro"];
const unidadesMaterial = ["chapa", "metro", "unidade", "par", "diaria", "conjunto", "pacote"];
const ORCAMENTO_RASCUNHO_KEY = "marceneiro_pro_orcamento_rascunho_v1";

const vazioOrcamento: Orcamento = {
  cliente: 0,
  nome_projeto: "",
  tipo_movel: "guarda_roupa",
  largura_mm: 2400,
  altura_mm: 2600,
  profundidade_mm: 600,
  descricao: "",
  material_principal: null,
  material_fundo: null,
  quantidade_portas: 3,
  tipo_porta: "correr",
  quantidade_gavetas: 4,
  quantidade_prateleiras: 6,
  quantidade_divisorias: 3,
  quantidade_cabideiros: 2,
  portas_basculantes: 0,
  quantidade_nichos: 0,
  usar_retalhos: true,
  kerf_mm: 3,
  perda_tecnica_percentual: 10,
  margem_desejada_percentual: 35,
  valor_mao_obra: 0,
  quantidade_diarias: 5,
  valor_diaria: 280,
  valor_instalacao: 300,
  valor_frete: 120,
  custos_extras: 0,
  preco_final_manual: null,
  validade_dias: 15,
  mostrar_detalhamento_pdf_cliente: false
};

const orcamentoLimpo: Orcamento = {
  ...vazioOrcamento,
  cliente: 0,
  nome_projeto: "",
  largura_mm: 0,
  altura_mm: 0,
  profundidade_mm: 0,
  material_principal: null,
  material_fundo: null,
  quantidade_portas: 0,
  quantidade_gavetas: 0,
  quantidade_prateleiras: 0,
  quantidade_divisorias: 0,
  quantidade_cabideiros: 0,
  kerf_mm: 0,
  perda_tecnica_percentual: 0,
  margem_desejada_percentual: 0,
  quantidade_diarias: 0,
  valor_diaria: 0,
  valor_instalacao: 0,
  valor_frete: 0,
  usar_retalhos: false,
  preco_final_manual: null
};

type OrcamentoRascunho = {
  form: Orcamento;
  editandoOrcamentoId: number | null;
};

function prepararFormOrcamento(base?: Partial<Orcamento>): Orcamento {
  const origem = base || {};
  return {
    cliente: Number(origem.cliente ?? vazioOrcamento.cliente),
    nome_projeto: origem.nome_projeto ?? vazioOrcamento.nome_projeto,
    tipo_movel: origem.tipo_movel ?? vazioOrcamento.tipo_movel,
    largura_mm: Number(origem.largura_mm ?? vazioOrcamento.largura_mm),
    altura_mm: Number(origem.altura_mm ?? vazioOrcamento.altura_mm),
    profundidade_mm: Number(origem.profundidade_mm ?? vazioOrcamento.profundidade_mm),
    descricao: origem.descricao ?? vazioOrcamento.descricao,
    status: origem.status ?? vazioOrcamento.status,
    material_principal: (origem.material_principal as number | null | undefined) ?? vazioOrcamento.material_principal,
    material_fundo: (origem.material_fundo as number | null | undefined) ?? vazioOrcamento.material_fundo,
    quantidade_portas: Number(origem.quantidade_portas ?? vazioOrcamento.quantidade_portas),
    tipo_porta: origem.tipo_porta ?? vazioOrcamento.tipo_porta,
    quantidade_gavetas: Number(origem.quantidade_gavetas ?? vazioOrcamento.quantidade_gavetas),
    quantidade_prateleiras: Number(origem.quantidade_prateleiras ?? vazioOrcamento.quantidade_prateleiras),
    quantidade_divisorias: Number(origem.quantidade_divisorias ?? vazioOrcamento.quantidade_divisorias),
    quantidade_cabideiros: Number(origem.quantidade_cabideiros ?? vazioOrcamento.quantidade_cabideiros),
    portas_basculantes: Number(origem.portas_basculantes ?? vazioOrcamento.portas_basculantes),
    quantidade_nichos: Number(origem.quantidade_nichos ?? vazioOrcamento.quantidade_nichos),
    usar_retalhos: Boolean(origem.usar_retalhos ?? vazioOrcamento.usar_retalhos),
    kerf_mm: Number(origem.kerf_mm ?? vazioOrcamento.kerf_mm),
    perda_tecnica_percentual: Number(origem.perda_tecnica_percentual ?? vazioOrcamento.perda_tecnica_percentual),
    margem_desejada_percentual: Number(origem.margem_desejada_percentual ?? vazioOrcamento.margem_desejada_percentual),
    valor_mao_obra: Number(origem.valor_mao_obra ?? vazioOrcamento.valor_mao_obra),
    quantidade_diarias: Number(origem.quantidade_diarias ?? vazioOrcamento.quantidade_diarias),
    valor_diaria: Number(origem.valor_diaria ?? vazioOrcamento.valor_diaria),
    valor_instalacao: Number(origem.valor_instalacao ?? vazioOrcamento.valor_instalacao),
    valor_frete: Number(origem.valor_frete ?? vazioOrcamento.valor_frete),
    custos_extras: Number(origem.custos_extras ?? vazioOrcamento.custos_extras),
    preco_final_manual: origem.preco_final_manual ?? null,
    validade_dias: Number(origem.validade_dias ?? vazioOrcamento.validade_dias),
    mostrar_detalhamento_pdf_cliente: Boolean(origem.mostrar_detalhamento_pdf_cliente ?? false)
  };
}

function carregarRascunhoOrcamento(): OrcamentoRascunho | null {
  try {
    if (typeof window === "undefined") return null;
    const bruto = window.localStorage.getItem(ORCAMENTO_RASCUNHO_KEY);
    if (!bruto) return null;
    const dado = JSON.parse(bruto) as Partial<OrcamentoRascunho>;
    if (!dado.form) return null;
    return {
      form: prepararFormOrcamento(dado.form),
      editandoOrcamentoId: dado.editandoOrcamentoId ?? null
    };
  } catch {
    return null;
  }
}

function salvarRascunhoOrcamento(dado: OrcamentoRascunho): void {
  try {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(ORCAMENTO_RASCUNHO_KEY, JSON.stringify(dado));
  } catch {
    // Ignora falha de persistencia local no navegador.
  }
}

function App() {
  const [aba, setAba] = useState<Aba>("dashboard");
  const [erro, setErro] = useState("");

  return (
    <div className="layout">
      <header className="header">
        <div>
          <h1 className="title">Marceneiro Pro</h1>
          <p className="subtitle">Orçamentos avançados de móveis planejados</p>
        </div>
      </header>

      <div className="tabs">
        <button className={aba === "dashboard" ? "active" : ""} onClick={() => setAba("dashboard")}>
          Dashboard
        </button>
        <button className={aba === "clientes" ? "active" : ""} onClick={() => setAba("clientes")}>
          Clientes
        </button>
        <button className={aba === "materiais" ? "active" : ""} onClick={() => setAba("materiais")}>
          Materiais
        </button>
        <button className={aba === "retalhos" ? "active" : ""} onClick={() => setAba("retalhos")}>
          Retalhos
        </button>
        <button className={aba === "orcamentos" ? "active" : ""} onClick={() => setAba("orcamentos")}>
          Orçamentos
        </button>
      </div>

      {erro && (
        <div className="card alert-item">
          <div className="row-between">
            <span>{erro}</span>
            <button className="secondary" onClick={() => setErro("")}>
              Fechar aviso
            </button>
          </div>
        </div>
      )}

      {aba === "dashboard" && <Dashboard onErro={setErro} />}
      {aba === "clientes" && <ClientesPage onErro={setErro} />}
      {aba === "materiais" && <MateriaisPage onErro={setErro} />}
      {aba === "retalhos" && <RetalhosPage onErro={setErro} />}
      {aba === "orcamentos" && <OrcamentosPage onErro={setErro} />}
    </div>
  );
}

function Dashboard({ onErro }: { onErro: (s: string) => void }) {
  const [dados, setDados] = useState<DashboardResumo | null>(null);
  const [carregando, setCarregando] = useState(true);
  useEffect(() => {
    setCarregando(true);
    api
      .get<DashboardResumo>("/dashboard/")
      .then(setDados)
      .catch((e) => onErro(String(e)))
      .finally(() => setCarregando(false));
  }, [onErro]);

  if (carregando) return <div className="card">Carregando dashboard...</div>;
  if (!dados) return <EstadoVazio titulo="Sem dados ainda" descricao="Cadastre um orçamento para começar." />;

  return (
    <div>
      <BlocoTitulo
        titulo="Visão geral do negócio"
        descricao="Aqui você acompanha quantos orçamentos estão em cada etapa e quanto pode faturar."
      />
      <div className="grid">
        <Kpi titulo="Orçamentos" valor={dados.quantidade_orcamentos} />
        <Kpi titulo="Rascunhos" valor={dados.orcamentos_rascunho} />
        <Kpi titulo="Calculados" valor={dados.orcamentos_calculados} />
        <Kpi titulo="Aprovados" valor={dados.orcamentos_aprovados} />
        <Kpi titulo="Faturamento potencial" valor={moeda(dados.faturamento_potencial)} />
        <Kpi titulo="Lucro potencial" valor={moeda(dados.lucro_estimado_potencial)} />
      </div>
    </div>
  );
}

function Kpi({ titulo, valor }: { titulo: string; valor: string | number }) {
  return (
    <div className="kpi">
      <h4>{titulo}</h4>
      <p>{valor}</p>
    </div>
  );
}

function Campo({
  label,
  ajuda,
  children,
  obrigatorio = false
}: {
  label: string;
  ajuda?: string;
  children: ReactNode;
  obrigatorio?: boolean;
}) {
  return (
    <label className="campo-formulario">
      <span className="campo-label">
        {label} {obrigatorio && <strong>*</strong>}
      </span>
      {children}
      {ajuda && <span className="campo-ajuda">{ajuda}</span>}
    </label>
  );
}

function BlocoTitulo({ titulo, descricao }: { titulo: string; descricao: string }) {
  return (
    <div className="bloco-titulo">
      <h3>{titulo}</h3>
      <p className="tiny">{descricao}</p>
    </div>
  );
}

function EstadoVazio({ titulo, descricao }: { titulo: string; descricao: string }) {
  return (
    <div className="estado-vazio">
      <h4>{titulo}</h4>
      <p>{descricao}</p>
    </div>
  );
}

function moeda(valor: number) {
  return `R$ ${Number(valor || 0).toFixed(2)}`;
}

function ClientesPage({ onErro }: { onErro: (s: string) => void }) {
  const [lista, setLista] = useState<Cliente[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [busca, setBusca] = useState("");
  const [form, setForm] = useState<Cliente>({ nome: "", telefone: "", endereco: "", observacoes: "" });
  const [editandoId, setEditandoId] = useState<number | null>(null);

  const carregar = () => {
    setCarregando(true);
    return api
      .get<Cliente[]>("/clientes/")
      .then(setLista)
      .catch((e) => onErro(String(e)))
      .finally(() => setCarregando(false));
  };

  useEffect(() => {
    carregar();
  }, []);

  const salvar = async (e: FormEvent) => {
    e.preventDefault();
    try {
      if (editandoId) {
        await api.put(`/clientes/${editandoId}/`, form);
      } else {
        await api.post("/clientes/", form);
      }
      setForm({ nome: "", telefone: "", endereco: "", observacoes: "" });
      setEditandoId(null);
      carregar();
    } catch (err) {
      onErro(String(err));
    }
  };

  return (
    <div className="card">
      <BlocoTitulo
        titulo="Clientes"
        descricao="Cadastre os dados básicos do cliente para reaproveitar nos próximos orçamentos."
      />
      <form onSubmit={salvar}>
        <div className="form-grid">
          <Campo label="Nome do cliente" obrigatorio>
            <input value={form.nome} placeholder="Ex.: João Carlos" onChange={(e) => setForm({ ...form, nome: e.target.value })} required />
          </Campo>
          <Campo label="Telefone">
            <input value={form.telefone} placeholder="Ex.: (11) 99999-9999" onChange={(e) => setForm({ ...form, telefone: e.target.value })} />
          </Campo>
          <Campo label="Endereço">
            <input value={form.endereco} placeholder="Rua, número e bairro" onChange={(e) => setForm({ ...form, endereco: e.target.value })} />
          </Campo>
        </div>
        <Campo label="Observações">
          <textarea
            value={form.observacoes}
            placeholder="Observações importantes do atendimento"
            onChange={(e) => setForm({ ...form, observacoes: e.target.value })}
          />
        </Campo>
        <button className="primary" type="submit">
          {editandoId ? "Atualizar cliente" : "Cadastrar cliente"}
        </button>
      </form>
      <div className="barra-filtro">
        <input
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          placeholder="Buscar cliente por nome"
          aria-label="Buscar cliente por nome"
        />
      </div>
      {carregando ? (
        <p>Carregando clientes...</p>
      ) : lista.length === 0 ? (
        <EstadoVazio titulo="Nenhum cliente cadastrado" descricao="Cadastre o primeiro cliente usando o formulário acima." />
      ) : (
      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Telefone</th>
            <th>Endereço</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {lista
            .filter((c) => c.nome.toLowerCase().includes(busca.toLowerCase()))
            .map((c) => (
            <tr key={c.id}>
              <td>{c.nome}</td>
              <td>{c.telefone}</td>
              <td>{c.endereco}</td>
              <td className="row-actions">
                <button
                  className="secondary"
                  onClick={() => {
                    setEditandoId(c.id || null);
                    setForm(c);
                  }}
                >
                  Editar
                </button>
                <button
                  className="danger"
                  onClick={async () => {
                    if (!window.confirm(`Deseja excluir o cliente ${c.nome}?`)) return;
                    await api.del(`/clientes/${c.id}/`);
                    carregar();
                  }}
                >
                  Excluir
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      )}
    </div>
  );
}

function MateriaisPage({ onErro }: { onErro: (s: string) => void }) {
  const [lista, setLista] = useState<Material[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [filtro, setFiltro] = useState("");
  const [busca, setBusca] = useState("");
  const [form, setForm] = useState<Material>({
    nome: "",
    tipo: "mdf",
    espessura_mm: 18,
    largura_mm: 2750,
    altura_mm: 1850,
    unidade: "chapa",
    preco_unitario: 0,
    fornecedor: "",
    padrao_visual: "liso",
    permite_rotacao_padrao: true,
    sentido_veio: "indiferente",
    ativo: true
  });
  const [editandoId, setEditandoId] = useState<number | null>(null);

  const carregar = () => {
    setCarregando(true);
    return api
      .get<Material[]>("/materiais/")
      .then(setLista)
      .catch((e) => onErro(String(e)))
      .finally(() => setCarregando(false));
  };

  useEffect(() => {
    carregar();
  }, []);

  const salvar = async (e: FormEvent) => {
    e.preventDefault();
    try {
      if (editandoId) {
        await api.put(`/materiais/${editandoId}/`, form);
      } else {
        await api.post("/materiais/", form);
      }
      setEditandoId(null);
      carregar();
    } catch (err) {
      onErro(String(err));
    }
  };

  const filtrados = useMemo(() => {
    const porTipo = filtro ? lista.filter((m) => m.tipo === filtro) : lista;
    return porTipo.filter((m) => m.nome.toLowerCase().includes(busca.toLowerCase()));
  }, [lista, filtro, busca]);

  return (
    <div className="card">
      <BlocoTitulo
        titulo="Materiais"
        descricao="Cadastre chapas, ferragens e insumos com preço para o cálculo ficar preciso."
      />
      <form onSubmit={salvar}>
        <div className="form-grid">
          <Campo label="Nome do material" obrigatorio>
            <input value={form.nome} placeholder="Ex.: MDF branco TX 18 mm" onChange={(e) => setForm({ ...form, nome: e.target.value })} required />
          </Campo>
          <Campo label="Tipo de material">
            <select value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}>
              {tiposMaterial.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </Campo>
          <Campo label="Espessura (mm)">
            <input
              type="number"
              value={form.espessura_mm}
              onChange={(e) => setForm({ ...form, espessura_mm: Number(e.target.value) })}
              placeholder="Ex.: 18"
            />
          </Campo>
          <Campo label="Largura da chapa (mm)">
            <input
              type="number"
              value={form.largura_mm}
              onChange={(e) => setForm({ ...form, largura_mm: Number(e.target.value) })}
              placeholder="Ex.: 2750"
            />
          </Campo>
          <Campo label="Altura da chapa (mm)">
            <input
              type="number"
              value={form.altura_mm}
              onChange={(e) => setForm({ ...form, altura_mm: Number(e.target.value) })}
              placeholder="Ex.: 1850"
            />
          </Campo>
          <Campo label="Unidade">
            <select value={form.unidade} onChange={(e) => setForm({ ...form, unidade: e.target.value })}>
              {unidadesMaterial.map((u) => (
                <option key={u} value={u}>
                  {u}
                </option>
              ))}
            </select>
          </Campo>
          <Campo label="Preço unitário (R$)">
            <input
              type="number"
              step="0.01"
              value={form.preco_unitario}
              onChange={(e) => setForm({ ...form, preco_unitario: Number(e.target.value) })}
              placeholder="Ex.: 349.90"
            />
          </Campo>
          <Campo label="Fornecedor">
            <input value={form.fornecedor} onChange={(e) => setForm({ ...form, fornecedor: e.target.value })} placeholder="Nome do fornecedor" />
          </Campo>
        </div>
        <button className="primary" type="submit">
          {editandoId ? "Atualizar material" : "Cadastrar material"}
        </button>
      </form>

      <div className="barra-filtro">
        <input value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Buscar material por nome" />
        <select value={filtro} onChange={(e) => setFiltro(e.target.value)}>
          <option value="">Todos os tipos</option>
          {tiposMaterial.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </div>
      {carregando ? (
        <p>Carregando materiais...</p>
      ) : filtrados.length === 0 ? (
        <EstadoVazio titulo="Nenhum material encontrado" descricao="Cadastre um material ou ajuste os filtros." />
      ) : (
      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Tipo</th>
            <th>Espessura</th>
            <th>Preço</th>
            <th>Ativo</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {filtrados.map((m) => (
            <tr key={m.id}>
              <td>{m.nome}</td>
              <td>{m.tipo}</td>
              <td>{m.espessura_mm} mm</td>
              <td>R$ {Number(m.preco_unitario).toFixed(2)}</td>
              <td>{m.ativo ? "Sim" : "Não"}</td>
              <td className="row-actions">
                <button
                  className="secondary"
                  onClick={() => {
                    setEditandoId(m.id || null);
                    setForm(m);
                  }}
                >
                  Editar
                </button>
                <button
                  className="secondary"
                  onClick={async () => {
                    await api.put(`/materiais/${m.id}/`, { ...m, ativo: !m.ativo });
                    carregar();
                  }}
                >
                  {m.ativo ? "Desativar" : "Ativar"}
                </button>
                <button
                  className="danger"
                  onClick={async () => {
                    if (!window.confirm(`Deseja excluir o material ${m.nome}?`)) return;
                    await api.del(`/materiais/${m.id}/`);
                    carregar();
                  }}
                >
                  Excluir
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      )}
    </div>
  );
}

function RetalhosPage({ onErro }: { onErro: (s: string) => void }) {
  const [materiais, setMateriais] = useState<Material[]>([]);
  const [lista, setLista] = useState<Retalho[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [busca, setBusca] = useState("");
  const [form, setForm] = useState<Retalho>({
    material: 0,
    largura_mm: 900,
    altura_mm: 650,
    origem: "",
    observacoes: "",
    disponivel: true
  });
  const [filtroMaterial, setFiltroMaterial] = useState(0);

  const carregar = async () => {
    setCarregando(true);
    try {
      const [mats, rets] = await Promise.all([api.get<Material[]>("/materiais/"), api.get<Retalho[]>("/retalhos/")]);
      setMateriais(mats);
      setLista(rets);
      if (!form.material && mats.length) setForm((prev) => ({ ...prev, material: mats[0].id || 0 }));
    } finally {
      setCarregando(false);
    }
  };

  useEffect(() => {
    carregar().catch((e) => onErro(String(e)));
  }, []);

  const salvar = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/retalhos/", form);
      carregar();
    } catch (err) {
      onErro(String(err));
    }
  };

  const filtrados = (filtroMaterial ? lista.filter((r) => r.material === filtroMaterial) : lista).filter((r) =>
    `${r.material_nome || ""} ${r.origem || ""}`.toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <div className="card">
      <BlocoTitulo
        titulo="Retalhos"
        descricao="Registre sobras de chapas para o sistema tentar aproveitar no cálculo e reduzir custos."
      />
      <form onSubmit={salvar}>
        <div className="form-grid">
          <Campo label="Material do retalho" obrigatorio>
            <select value={form.material} onChange={(e) => setForm({ ...form, material: Number(e.target.value) })}>
              {materiais.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.nome}
                </option>
              ))}
            </select>
          </Campo>
          <Campo label="Largura do retalho (mm)" obrigatorio>
            <input
              type="number"
              value={form.largura_mm}
              onChange={(e) => setForm({ ...form, largura_mm: Number(e.target.value) })}
              placeholder="Ex.: 900"
            />
          </Campo>
          <Campo label="Altura do retalho (mm)" obrigatorio>
            <input
              type="number"
              value={form.altura_mm}
              onChange={(e) => setForm({ ...form, altura_mm: Number(e.target.value) })}
              placeholder="Ex.: 650"
            />
          </Campo>
          <Campo label="Origem">
            <input value={form.origem} onChange={(e) => setForm({ ...form, origem: e.target.value })} placeholder="Ex.: sobra do projeto João" />
          </Campo>
        </div>
        <button className="primary" type="submit">
          Cadastrar retalho
        </button>
      </form>
      <div className="barra-filtro">
        <input value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Buscar por material ou origem" />
        <select value={filtroMaterial} onChange={(e) => setFiltroMaterial(Number(e.target.value))}>
          <option value={0}>Todos os materiais</option>
          {materiais.map((m) => (
            <option key={m.id} value={m.id}>
              {m.nome}
            </option>
          ))}
        </select>
      </div>
      {carregando ? (
        <p>Carregando retalhos...</p>
      ) : filtrados.length === 0 ? (
        <EstadoVazio titulo="Nenhum retalho encontrado" descricao="Cadastre um retalho ou ajuste os filtros." />
      ) : (
      <table>
        <thead>
          <tr>
            <th>Material</th>
            <th>Medidas</th>
            <th>Origem</th>
            <th>Disponível</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {filtrados.map((r) => (
            <tr key={r.id}>
              <td>{r.material_nome}</td>
              <td>
                {r.largura_mm} x {r.altura_mm}
              </td>
              <td>{r.origem}</td>
              <td>{r.disponivel ? "Sim" : "Não"}</td>
              <td>
                <button
                  className="secondary"
                  onClick={async () => {
                    const novoStatus = !r.disponivel;
                    const msg = novoStatus
                      ? "Marcar este retalho como disponível novamente?"
                      : "Marcar este retalho como indisponível?";
                    if (!window.confirm(msg)) return;
                    await api.put(`/retalhos/${r.id}/`, { ...r, disponivel: novoStatus });
                    carregar();
                  }}
                >
                  {r.disponivel ? "Marcar indisponível" : "Marcar disponível"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      )}
    </div>
  );
}

function OrcamentosPage({ onErro }: { onErro: (s: string) => void }) {
  const rascunhoInicial = useMemo(() => carregarRascunhoOrcamento(), []);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [materiais, setMateriais] = useState<Material[]>([]);
  const [orcamentos, setOrcamentos] = useState<Orcamento[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [buscaOrcamento, setBuscaOrcamento] = useState("");
  const [form, setForm] = useState<Orcamento>(rascunhoInicial?.form || vazioOrcamento);
  const [editandoOrcamentoId, setEditandoOrcamentoId] = useState<number | null>(rascunhoInicial?.editandoOrcamentoId || null);
  const [rascunhoRestaurado] = useState<boolean>(Boolean(rascunhoInicial));
  const [recalculandoId, setRecalculandoId] = useState<number | null>(null);
  const [resultado, setResultado] = useState<any>(null);
  const [abaResultado, setAbaResultado] = useState("resumo");

  const limparFormularioOrcamento = () => {
    setEditandoOrcamentoId(null);
    setForm(prepararFormOrcamento(orcamentoLimpo));
    setResultado(null);
  };

  const carregar = async () => {
    setCarregando(true);
    try {
      const [c, m, o] = await Promise.all([
        api.get<Cliente[]>("/clientes/"),
        api.get<Material[]>("/materiais/"),
        api.get<Orcamento[]>("/orcamentos/")
      ]);
      setClientes(c);
      setMateriais(m);
      setOrcamentos(o);
      if (!form.cliente && c.length) setForm((prev) => ({ ...prev, cliente: c[0].id || 0 }));
      if (!form.material_principal && m.length) setForm((prev) => ({ ...prev, material_principal: m[0].id || null }));
      if (!form.material_fundo && m.length > 1) setForm((prev) => ({ ...prev, material_fundo: m[1].id || null }));
    } finally {
      setCarregando(false);
    }
  };

  useEffect(() => {
    carregar().catch((e) => onErro(String(e)));
  }, []);

  useEffect(() => {
    salvarRascunhoOrcamento({
      form,
      editandoOrcamentoId,
    });
  }, [form, editandoOrcamentoId]);

  const criarOrcamento = async (e: FormEvent) => {
    e.preventDefault();
    try {
      if (editandoOrcamentoId) {
        await api.put(`/orcamentos/${editandoOrcamentoId}/`, form);
      } else {
        await api.post("/orcamentos/", form);
      }
      limparFormularioOrcamento();
      carregar();
    } catch (err) {
      onErro(String(err));
    }
  };

  const calcular = async (id?: number) => {
    if (!id) return;
    try {
      setRecalculandoId(id);
      const data = await api.post<any>(`/orcamentos/${id}/calcular/`);
      setResultado({ ...data, orcamento_id: id });
      setAbaResultado("resumo");
      await carregar();
    } catch (err) {
      onErro(String(err));
    } finally {
      setRecalculandoId(null);
    }
  };

  const preencherExemplo = (tipo: "guarda_roupa" | "painel_tv" | "armario_aereo") => {
    if (tipo === "guarda_roupa") {
      setForm((prev) => ({
        ...prev,
        tipo_movel: "guarda_roupa",
        nome_projeto: "Guarda-roupa do cliente",
        largura_mm: 2400,
        altura_mm: 2600,
        profundidade_mm: 600,
        quantidade_portas: 3,
        tipo_porta: "correr",
        quantidade_gavetas: 4,
        quantidade_prateleiras: 6,
        quantidade_divisorias: 3,
        quantidade_cabideiros: 2
      }));
    }
    if (tipo === "painel_tv") {
      setForm((prev) => ({
        ...prev,
        tipo_movel: "painel_tv",
        nome_projeto: "Painel de TV do cliente",
        largura_mm: 1800,
        altura_mm: 1600,
        profundidade_mm: 400,
        quantidade_portas: 2,
        tipo_porta: "basculante",
        quantidade_gavetas: 0,
        quantidade_prateleiras: 0,
        quantidade_divisorias: 2,
        quantidade_cabideiros: 0
      }));
    }
    if (tipo === "armario_aereo") {
      setForm((prev) => ({
        ...prev,
        tipo_movel: "armario_aereo",
        nome_projeto: "Armário aéreo do cliente",
        largura_mm: 1200,
        altura_mm: 700,
        profundidade_mm: 320,
        quantidade_portas: 3,
        tipo_porta: "abrir",
        quantidade_gavetas: 0,
        quantidade_prateleiras: 1,
        quantidade_divisorias: 0,
        quantidade_cabideiros: 0
      }));
    }
  };

  const orcamentosFiltrados = orcamentos.filter((o) =>
    `${o.nome_projeto} ${o.cliente_nome || ""} ${o.status || ""}`.toLowerCase().includes(buscaOrcamento.toLowerCase())
  );

  return (
    <div className="card">
      <BlocoTitulo
        titulo={editandoOrcamentoId ? "Editar orçamento" : "Novo orçamento"}
        descricao="Preencha os dados em sequência. Se preferir, clique em um exemplo para começar com valores prontos."
      />
      {rascunhoRestaurado && <p className="tiny">Rascunho restaurado automaticamente.</p>}
      <div className="row-actions" style={{ marginBottom: 10 }}>
        <button className="secondary" type="button" onClick={() => preencherExemplo("guarda_roupa")}>
          Exemplo: Guarda-roupa
        </button>
        <button className="secondary" type="button" onClick={() => preencherExemplo("painel_tv")}>
          Exemplo: Painel TV
        </button>
        <button className="secondary" type="button" onClick={() => preencherExemplo("armario_aereo")}>
          Exemplo: Armário aéreo
        </button>
      </div>
      <p className="tiny">
        Preencha com calma, em ordem. Primeiro salve o orçamento, depois clique em <strong>Calcular orçamento</strong>.
      </p>
      <div className="guia-rapido">
        <p>
          <strong>Guia rápido:</strong>
        </p>
        <ol>
          <li>Escolha o cliente e dê um nome para o projeto.</li>
          <li>Informe as medidas em milímetros (mm).</li>
          <li>Marque quantas portas, gavetas e prateleiras o móvel terá.</li>
          <li>Escolha os materiais.</li>
          <li>Informe margem e custos (instalação/frete).</li>
        </ol>
      </div>
      <form onSubmit={criarOrcamento}>
        <div className="secao-formulario">
          <h4>Etapa 1: Cliente e projeto</h4>
          <div className="form-grid">
            <Campo label="Cliente" ajuda="Selecione para quem este orçamento será feito." obrigatorio>
              <select required value={form.cliente} onChange={(e) => setForm({ ...form, cliente: Number(e.target.value) })}>
                <option value={0}>Selecione um cliente</option>
                {clientes.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.nome}
                  </option>
                ))}
              </select>
            </Campo>
            <Campo label="Nome do projeto" ajuda="Exemplo: Guarda-roupa quarto casal." obrigatorio>
              <input
                value={form.nome_projeto}
                onChange={(e) => setForm({ ...form, nome_projeto: e.target.value })}
                placeholder="Ex.: Guarda-roupa quarto casal"
                required
              />
            </Campo>
            <Campo label="Tipo de móvel" ajuda="Escolha o tipo mais próximo.">
              <select value={form.tipo_movel} onChange={(e) => setForm({ ...form, tipo_movel: e.target.value })}>
                <option value="guarda_roupa">Guarda-roupa</option>
                <option value="painel_tv">Painel de TV com rack</option>
                <option value="armario_aereo">Armário aéreo</option>
                <option value="outro">Outro</option>
              </select>
            </Campo>
          </div>
        </div>

        <div className="secao-formulario">
          <h4>Etapa 2: Medidas do móvel (mm)</h4>
          <div className="form-grid">
            <Campo label="Largura (mm)" ajuda="Medida da esquerda para a direita." obrigatorio>
              <input
                type="number"
                min={100}
                value={form.largura_mm || ""}
                onChange={(e) => setForm({ ...form, largura_mm: e.target.value ? Number(e.target.value) : 0 })}
              />
            </Campo>
            <Campo label="Altura (mm)" ajuda="Medida do chão para cima." obrigatorio>
              <input
                type="number"
                min={100}
                value={form.altura_mm || ""}
                onChange={(e) => setForm({ ...form, altura_mm: e.target.value ? Number(e.target.value) : 0 })}
              />
            </Campo>
            <Campo label="Profundidade (mm)" ajuda="Medida da frente para o fundo." obrigatorio>
              <input
                type="number"
                min={100}
                value={form.profundidade_mm || ""}
                onChange={(e) => setForm({ ...form, profundidade_mm: e.target.value ? Number(e.target.value) : 0 })}
              />
            </Campo>
          </div>
        </div>

        <div className="secao-formulario">
          <h4>Etapa 3: Configuração do móvel</h4>
          <div className="form-grid">
            <Campo label="Quantidade de portas" ajuda="Número total de portas.">
              <input
                type="number"
                min={0}
                value={form.quantidade_portas || ""}
                onChange={(e) => setForm({ ...form, quantidade_portas: e.target.value ? Number(e.target.value) : 0 })}
              />
            </Campo>
            <Campo label="Tipo de porta" ajuda="Abrir, correr, basculante ou nenhuma.">
              <select value={form.tipo_porta} onChange={(e) => setForm({ ...form, tipo_porta: e.target.value })}>
                <option value="abrir">Abrir</option>
                <option value="correr">Correr</option>
                <option value="basculante">Basculante</option>
                <option value="nenhuma">Nenhuma</option>
              </select>
            </Campo>
            <Campo label="Gavetas" ajuda="Quantas gavetas terá o móvel.">
              <input
                type="number"
                min={0}
                value={form.quantidade_gavetas || ""}
                onChange={(e) => setForm({ ...form, quantidade_gavetas: e.target.value ? Number(e.target.value) : 0 })}
              />
            </Campo>
            <Campo label="Prateleiras" ajuda="Número de prateleiras internas.">
              <input
                type="number"
                min={0}
                value={form.quantidade_prateleiras || ""}
                onChange={(e) => setForm({ ...form, quantidade_prateleiras: e.target.value ? Number(e.target.value) : 0 })}
              />
            </Campo>
            <Campo label="Divisórias" ajuda="Placas verticais internas.">
              <input
                type="number"
                min={0}
                value={form.quantidade_divisorias || ""}
                onChange={(e) => setForm({ ...form, quantidade_divisorias: e.target.value ? Number(e.target.value) : 0 })}
              />
            </Campo>
            <Campo label="Cabideiros" ajuda="Quantidade de tubos cabideiro.">
              <input
                type="number"
                min={0}
                value={form.quantidade_cabideiros || ""}
                onChange={(e) => setForm({ ...form, quantidade_cabideiros: e.target.value ? Number(e.target.value) : 0 })}
              />
            </Campo>
          </div>
        </div>

        <div className="secao-formulario">
          <h4>Etapa 4: Materiais e corte</h4>
          <div className="form-grid">
            <Campo label="Material principal" ajuda="Material usado no corpo do móvel." obrigatorio>
              <select
                required
                value={form.material_principal || 0}
                onChange={(e) => {
                  const valor = Number(e.target.value);
                  setForm({ ...form, material_principal: valor > 0 ? valor : null });
                }}
              >
                <option value={0}>Selecione um material principal</option>
                {materiais.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.nome}
                  </option>
                ))}
              </select>
            </Campo>
            <Campo label="Material do fundo" ajuda="Normalmente MDF de menor espessura.">
              <select
                value={form.material_fundo || 0}
                onChange={(e) => {
                  const valor = Number(e.target.value);
                  setForm({ ...form, material_fundo: valor > 0 ? valor : null });
                }}
              >
                <option value={0}>Selecione o material do fundo</option>
                {materiais.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.nome}
                  </option>
                ))}
              </select>
            </Campo>
            <Campo label="Espessura do corte (kerf mm)" ajuda="Espessura da serra. Padrão: 3 mm.">
              <input
                type="number"
                step="0.1"
                min={0}
                value={form.kerf_mm || ""}
                onChange={(e) => setForm({ ...form, kerf_mm: e.target.value ? Number(e.target.value) : 0 })}
              />
            </Campo>
            <Campo label="Perda técnica (%)" ajuda="Margem para perdas de corte. Padrão: 10%.">
              <input
                type="number"
                step="0.1"
                min={0}
                value={form.perda_tecnica_percentual || ""}
                onChange={(e) => setForm({ ...form, perda_tecnica_percentual: e.target.value ? Number(e.target.value) : 0 })}
              />
            </Campo>
          </div>
          <label className="checkbox-campo">
            <input
              type="checkbox"
              checked={form.usar_retalhos}
              onChange={(e) => setForm({ ...form, usar_retalhos: e.target.checked })}
            />
            <span>Usar retalhos disponíveis para tentar economizar material</span>
          </label>
        </div>

        <div className="secao-formulario">
          <h4>Etapa 5: Custos e preço de venda</h4>
          <div className="form-grid">
            <Campo label="Margem desejada (%)" ajuda="Exemplo comum: 35%.">
              <input
                type="number"
                step="0.1"
                min={0}
                value={form.margem_desejada_percentual || ""}
                onChange={(e) => setForm({ ...form, margem_desejada_percentual: e.target.value ? Number(e.target.value) : 0 })}
              />
            </Campo>
            <Campo label="Quantidade de diárias" ajuda="Quantos dias de trabalho serão usados.">
              <input
                type="number"
                min={0}
                value={form.quantidade_diarias || ""}
                onChange={(e) => setForm({ ...form, quantidade_diarias: e.target.value ? Number(e.target.value) : 0 })}
              />
            </Campo>
            <Campo label="Valor da diária (R$)" ajuda="Preço de 1 diária de trabalho.">
              <input
                type="number"
                step="0.01"
                min={0}
                value={form.valor_diaria || ""}
                onChange={(e) => setForm({ ...form, valor_diaria: e.target.value ? Number(e.target.value) : 0 })}
              />
            </Campo>
            <Campo label="Instalação (R$)" ajuda="Se não houver, deixe 0.">
              <input
                type="number"
                step="0.01"
                min={0}
                value={form.valor_instalacao || ""}
                onChange={(e) => setForm({ ...form, valor_instalacao: e.target.value ? Number(e.target.value) : 0 })}
              />
            </Campo>
            <Campo label="Frete (R$)" ajuda="Se não houver, deixe 0.">
              <input
                type="number"
                step="0.01"
                min={0}
                value={form.valor_frete || ""}
                onChange={(e) => setForm({ ...form, valor_frete: e.target.value ? Number(e.target.value) : 0 })}
              />
            </Campo>
            <Campo label="Preço final manual (R$)" ajuda="Opcional. Se preencher, o sistema recalcula lucro e margem real.">
              <input
                type="number"
                step="0.01"
                min={0}
                value={form.preco_final_manual || ""}
                onChange={(e) => setForm({ ...form, preco_final_manual: e.target.value ? Number(e.target.value) : null })}
                placeholder="Deixe vazio para usar preço sugerido"
              />
            </Campo>
          </div>
        </div>
        <button className="primary" type="submit">
          {editandoOrcamentoId ? "Salvar alterações do orçamento" : "Salvar orçamento (ainda não calcula)"}
        </button>
        <button className="secondary" type="button" onClick={limparFormularioOrcamento}>
          Limpar formulário
        </button>
        {editandoOrcamentoId && (
          <button
            className="secondary"
            type="button"
            onClick={() => {
              limparFormularioOrcamento();
            }}
          >
            Cancelar edição
          </button>
        )}
      </form>

      <h3 style={{ marginTop: 18 }}>Orçamentos cadastrados</h3>
      <div className="barra-filtro">
        <input
          value={buscaOrcamento}
          onChange={(e) => setBuscaOrcamento(e.target.value)}
          placeholder="Buscar por projeto, cliente ou status"
        />
      </div>
      {carregando ? (
        <p>Carregando orçamentos...</p>
      ) : orcamentosFiltrados.length === 0 ? (
        <EstadoVazio titulo="Nenhum orçamento encontrado" descricao="Crie um orçamento novo ou ajuste a busca." />
      ) : (
      <table>
        <thead>
          <tr>
            <th>Projeto</th>
            <th>Cliente</th>
            <th>Status</th>
            <th>Último cálculo</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {orcamentosFiltrados.map((o) => (
            <tr key={o.id}>
              <td>{o.nome_projeto}</td>
              <td>{o.cliente_nome}</td>
              <td>{o.status}</td>
              <td>{o.data_ultima_calculacao ? new Date(o.data_ultima_calculacao).toLocaleString("pt-BR") : "-"}</td>
              <td className="row-actions">
                <button
                  className="secondary"
                  onClick={() => {
                    setEditandoOrcamentoId(o.id || null);
                    setForm(prepararFormOrcamento(o));
                    window.scrollTo({ top: 0, behavior: "smooth" });
                  }}
                >
                  Editar
                </button>
                <button className="primary" onClick={() => calcular(o.id)} disabled={recalculandoId === o.id}>
                  {recalculandoId === o.id
                    ? "Calculando..."
                    : o.status === "calculado" || o.status === "aprovado" || o.status === "enviado" || o.status === "recusado"
                      ? "1) Recalcular"
                      : "1) Calcular"}
                </button>
                <button className="secondary" onClick={() => setResultado({ ...(o.resultado_calculo || {}), orcamento_id: o.id })}>
                  2) Ver resultado
                </button>
                <button
                  className="secondary"
                  onClick={async () => {
                    await api.post(`/orcamentos/${o.id}/aprovar/`);
                    carregar();
                  }}
                >
                  Aprovar
                </button>
                <button
                  className="secondary"
                  onClick={async () => {
                    await api.post(`/orcamentos/${o.id}/recusar/`);
                    carregar();
                  }}
                >
                  Recusar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      )}

      {resultado && (
        <div className="card" style={{ marginTop: 18 }}>
          <h3>Resultado do orçamento</h3>
          <div className="grid">
            <Kpi titulo="Custo total" valor={`R$ ${resultado.financeiro?.custo_total?.toFixed?.(2) ?? "0.00"}`} />
            <Kpi titulo="Preço sugerido" valor={`R$ ${resultado.financeiro?.preco_sugerido?.toFixed?.(2) ?? "0.00"}`} />
            <Kpi titulo="Preço final" valor={`R$ ${resultado.financeiro?.preco_final?.toFixed?.(2) ?? "0.00"}`} />
            <Kpi titulo="Lucro estimado" valor={`R$ ${resultado.financeiro?.lucro_estimado?.toFixed?.(2) ?? "0.00"}`} />
            <Kpi titulo="Margem real" valor={`${resultado.financeiro?.margem_real_percentual ?? 0}%`} />
            <Kpi titulo="Aproveitamento" valor={`${resultado.plano_corte?.aproveitamento_percentual?.toFixed?.(2) ?? 0}%`} />
            <Kpi titulo="Confiança" valor={`${resultado.alertas?.nota_confianca ?? 0}/100`} />
          </div>

          <div className="result-tabs">
            {[
              ["resumo", "Resumo"],
              ["pecas", "Peças"],
              ["plano", "Plano de corte"],
              ["retalhos", "Retalhos"],
              ["ferragens", "Ferragens"],
              ["fita", "Fita de borda"],
              ["lista", "Lista de compra"],
              ["ordem", "Ordem de produção"],
              ["alertas", "Alertas"],
              ["pagamentos", "Pagamentos"],
              ["pdfs", "PDFs"]
            ].map(([valor, rotulo]) => (
              <button key={valor} className={abaResultado === valor ? "active" : ""} onClick={() => setAbaResultado(valor)}>
                {rotulo}
              </button>
            ))}
          </div>

          {abaResultado === "resumo" && (
            <div>
              <p>
                Total de peças: <strong>{resultado.pecas?.length || 0}</strong>
              </p>
              <p>
                Itens de custo: <strong>{resultado.itens_custo?.length || 0}</strong>
              </p>
            </div>
          )}

          {abaResultado === "pecas" && (
            <table>
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Material</th>
                  <th>Medidas</th>
                  <th>Qtd</th>
                </tr>
              </thead>
              <tbody>
                {(resultado.pecas || []).map((p: any) => (
                  <tr key={p.id}>
                    <td>{p.nome}</td>
                    <td>{p.material_nome}</td>
                    <td>
                      {p.largura_mm} x {p.altura_mm}
                    </td>
                    <td>{p.quantidade}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {abaResultado === "plano" && (
            <PlanoCorteVisual
              planos={resultado.plano_corte?.planos || []}
              retalhosUsados={resultado.plano_corte?.retalhos_usados || resultado.retalhos?.retalhos_usados || []}
            />
          )}

          {abaResultado === "retalhos" && (
            <div>
              <p>Economia estimada: R$ {Number(resultado.retalhos?.economia_estimada || 0).toFixed(2)}</p>
              <p>Chapas economizadas: {resultado.retalhos?.chapas_economizadas_aprox || 0}</p>
              {(resultado.retalhos?.retalhos_usados || []).map((retalho: any) => (
                <div key={retalho.retalho_id} className="card">
                  <h4>
                    Retalho #{retalho.retalho_id} - {retalho.material} ({retalho.largura_mm} x {retalho.altura_mm} mm)
                  </h4>
                  <table>
                    <thead>
                      <tr>
                        <th>Peça</th>
                        <th>Medidas</th>
                        <th>Posição</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(retalho.pecas_atendidas || []).map((p: any, idx: number) => (
                        <tr key={idx}>
                          <td>{p.peca_nome}</td>
                          <td>
                            {p.largura_mm} x {p.altura_mm} mm
                          </td>
                          <td>
                            x={p.x ?? 0}, y={p.y ?? 0}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ))}
            </div>
          )}

          {abaResultado === "ferragens" && <ItensPorCategoria itens={resultado.itens_custo || []} categoria="ferragem" />}
          {abaResultado === "fita" && <ItensPorCategoria itens={resultado.itens_custo || []} categoria="fita" />}

          {abaResultado === "lista" && (
            <table>
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Quantidade</th>
                  <th>Unidade</th>
                  <th>Preço</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {(resultado.lista_compra || []).map((i: any, idx: number) => (
                  <tr key={idx}>
                    <td>{i.nome}</td>
                    <td>{i.quantidade}</td>
                    <td>{i.unidade}</td>
                    <td>R$ {Number(i.preco_unitario).toFixed(2)}</td>
                    <td>R$ {Number(i.total).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {abaResultado === "ordem" && (
            <ol>
              {(resultado.ordem_producao?.ordem_sugerida || []).map((p: string, idx: number) => (
                <li key={idx}>{p}</li>
              ))}
            </ol>
          )}

          {abaResultado === "alertas" && (
            <div>
              {(resultado.alertas?.alertas || []).map((a: string, idx: number) => (
                <div key={idx} className="alert-item">
                  {a}
                </div>
              ))}
            </div>
          )}

          {abaResultado === "pagamentos" && (
            <table>
              <thead>
                <tr>
                  <th>Descrição</th>
                  <th>Valor</th>
                </tr>
              </thead>
              <tbody>
                {(resultado.pagamentos || []).map((p: any, idx: number) => (
                  <tr key={idx}>
                    <td>{p.descricao}</td>
                    <td>R$ {Number(p.valor).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {abaResultado === "pdfs" && (
            <div className="row-actions">
              <a className="primary" href={api.fileUrl(`/orcamentos/${resultado.orcamento_id}/pdf_cliente/`)} target="_blank" rel="noreferrer">
                Gerar PDF cliente
              </a>
              <a className="secondary" href={api.fileUrl(`/orcamentos/${resultado.orcamento_id}/pdf_tecnico/`)} target="_blank" rel="noreferrer">
                Gerar PDF técnico
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ItensPorCategoria({ itens, categoria }: { itens: any[]; categoria: string }) {
  const filtrados = itens.filter((i) => i.categoria === categoria);
  if (!filtrados.length) return <EstadoVazio titulo="Nada para mostrar" descricao="Nenhum item calculado nesta categoria." />;
  return (
    <table>
      <thead>
        <tr>
          <th>Nome</th>
          <th>Quantidade</th>
          <th>Preço unitário</th>
          <th>Total</th>
        </tr>
      </thead>
      <tbody>
        {filtrados.map((i) => (
          <tr key={i.id}>
            <td>{i.nome}</td>
            <td>
              {i.quantidade} {i.unidade}
            </td>
            <td>R$ {Number(i.preco_unitario).toFixed(2)}</td>
            <td>R$ {Number(i.preco_total).toFixed(2)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function PlanoCorteVisual({ planos, retalhosUsados }: { planos: any[]; retalhosUsados: any[] }) {
  if (!planos.length && !retalhosUsados.length)
    return <EstadoVazio titulo="Sem plano de corte" descricao="Calcule o orçamento para gerar o plano de corte." />;
  return (
    <div>
      {planos.map((plano, idx) => (
        <div key={idx} className="card">
          <h4>
            {plano.material_nome} | {plano.quantidade_chapas} chapa(s) | Aproveitamento {Number(plano.aproveitamento_percentual).toFixed(2)}%
          </h4>
          {(plano.chapas || []).map((chapa: any) => (
            <CorteChapa key={chapa.indice} chapa={chapa} />
          ))}
        </div>
      ))}

      {retalhosUsados.length > 0 && (
        <div className="card">
          <h4>Plano de corte em retalhos</h4>
          {retalhosUsados.map((retalho: any) => (
            <CorteChapa
              key={`retalho-${retalho.retalho_id}`}
              chapa={{
                indice: `R${retalho.retalho_id}`,
                largura_mm: retalho.largura_mm,
                altura_mm: retalho.altura_mm,
                pecas: retalho.pecas_atendidas || [],
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function CorteChapa({ chapa }: { chapa: any }) {
  const maxW = 850;
  const escala = Math.min(maxW / chapa.largura_mm, 1);
  const largura = chapa.largura_mm * escala;
  const altura = chapa.altura_mm * escala;

  return (
    <div className="cut-sheet" style={{ width: largura + 8 }}>
      <div className="cut-inner" style={{ width: largura, height: Math.max(altura, 220) }}>
        {(chapa.pecas || []).map((p: any, idx: number) => (
          <div
            className="cut-piece"
            key={idx}
            style={{
              left: p.x * escala,
              top: p.y * escala,
              width: p.largura_mm * escala,
              height: p.altura_mm * escala
            }}
            title={`${p.nome || p.peca_nome} ${p.largura_mm}x${p.altura_mm}`}
          >
            {p.nome || p.peca_nome}
          </div>
        ))}
      </div>
      <p className="tiny">
        Chapa {chapa.indice} ({chapa.largura_mm} x {chapa.altura_mm} mm)
      </p>
    </div>
  );
}

export default App;
