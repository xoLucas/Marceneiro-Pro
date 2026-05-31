export type DashboardResumo = {
  quantidade_orcamentos: number;
  orcamentos_rascunho: number;
  orcamentos_calculados: number;
  orcamentos_aprovados: number;
  faturamento_potencial: number;
  lucro_estimado_potencial: number;
};

export type Cliente = {
  id?: number;
  nome: string;
  telefone?: string;
  endereco?: string;
  observacoes?: string;
};

export type Material = {
  id?: number;
  nome: string;
  tipo: string;
  espessura_mm: number;
  largura_mm: number;
  altura_mm: number;
  unidade: string;
  preco_unitario: number;
  fornecedor?: string;
  padrao_visual: string;
  permite_rotacao_padrao: boolean;
  sentido_veio: string;
  ativo: boolean;
};

export type Retalho = {
  id?: number;
  material: number;
  material_nome?: string;
  largura_mm: number;
  altura_mm: number;
  origem?: string;
  observacoes?: string;
  disponivel: boolean;
};

export type Orcamento = {
  id?: number;
  cliente: number;
  cliente_nome?: string;
  nome_projeto: string;
  tipo_movel: string;
  largura_mm: number;
  altura_mm: number;
  profundidade_mm: number;
  descricao?: string;
  status?: string;
  material_principal?: number | null;
  material_fundo?: number | null;
  quantidade_portas: number;
  tipo_porta: string;
  quantidade_gavetas: number;
  quantidade_prateleiras: number;
  quantidade_divisorias: number;
  quantidade_cabideiros: number;
  portas_basculantes: number;
  quantidade_nichos: number;
  usar_retalhos: boolean;
  kerf_mm: number;
  perda_tecnica_percentual: number;
  margem_desejada_percentual: number;
  valor_mao_obra: number;
  quantidade_diarias: number;
  valor_diaria: number;
  valor_instalacao: number;
  valor_frete: number;
  custos_extras: number;
  preco_final_manual?: number | null;
  validade_dias: number;
  mostrar_detalhamento_pdf_cliente: boolean;
  resultado_calculo?: any;
  nota_confianca?: number;
  data_ultima_calculacao?: string | null;
};
