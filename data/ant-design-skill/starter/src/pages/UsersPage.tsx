import React, { useEffect, useMemo, useState } from 'react';
import {
  Button,
  Card,
  Col,
  Drawer,
  Form,
  Input,
  message,
  Popconfirm,
  Row,
  Select,
  Space,
  Switch,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table';
import { createUser, deleteUser, listUsers, updateUser } from './mockServer';
import type { UpsertUserInput, User, UserListFilters } from './types';

export function UsersPage() {
  const [filtersForm] = Form.useForm<UserListFilters>();
  const [editForm] = Form.useForm<UpsertUserInput>();

  const [filters, setFilters] = useState<UserListFilters>({ active: 'all' });
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<User[]>([]);
  const [total, setTotal] = useState(0);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editing, setEditing] = useState<User | null>(null);
  const drawerTitle = editing ? 'Editar usuário' : 'Novo usuário';

  const columns: ColumnsType<User> = useMemo(
    () => [
      {
        title: 'Nome',
        dataIndex: 'name',
        key: 'name',
        render: (v: string) => <Typography.Text strong>{v}</Typography.Text>,
      },
      {
        title: 'Email',
        dataIndex: 'email',
        key: 'email',
        render: (v: string) => <Typography.Text type="secondary">{v}</Typography.Text>,
      },
      {
        title: 'Role',
        dataIndex: 'role',
        key: 'role',
        render: (role: User['role']) => (
          <Tag color={role === 'admin' ? 'geekblue' : 'default'}>{role}</Tag>
        ),
        width: 120,
      },
      {
        title: 'Status',
        dataIndex: 'active',
        key: 'active',
        render: (active: boolean) => (
          <Tag color={active ? 'green' : 'red'}>{active ? 'Ativo' : 'Inativo'}</Tag>
        ),
        width: 120,
      },
      {
        title: 'Ações',
        key: 'actions',
        width: 160,
        render: (_: any, row: User) => (
          <Space size="middle">
            <Button size="small" onClick={() => openEdit(row)}>
              Editar
            </Button>
            <Popconfirm
              title="Excluir usuário?"
              description="Essa ação não pode ser desfeita."
              okText="Excluir"
              cancelText="Cancelar"
              onConfirm={() => onDelete(row)}
            >
              <Button danger size="small">
                Excluir
              </Button>
            </Popconfirm>
          </Space>
        ),
      },
    ],
    []
  );

  async function refresh() {
    setLoading(true);
    try {
      const res = await listUsers({ page, pageSize, filters });
      setItems(res.items);
      setTotal(res.total);
    } catch (e: any) {
      message.error(e?.message || 'Erro ao carregar usuários');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, filters]);

  function applyFilters(values: UserListFilters) {
    const normalized: UserListFilters = {
      q: values.q?.trim() || undefined,
      role: values.role || undefined,
      active: values.active ?? 'all',
    };
    setPage(1);
    setFilters(normalized);
  }

  function clearFilters() {
    filtersForm.resetFields();
    applyFilters({ active: 'all' });
  }

  function openCreate() {
    setEditing(null);
    editForm.resetFields();
    editForm.setFieldsValue({ role: 'user', active: true, name: '', email: '' });
    setDrawerOpen(true);
  }

  function openEdit(user: User) {
    setEditing(user);
    editForm.setFieldsValue({
      name: user.name,
      email: user.email,
      role: user.role,
      active: user.active,
    });
    setDrawerOpen(true);
  }

  async function onSave() {
    try {
      const values = await editForm.validateFields();
      if (editing) {
        await updateUser(editing.id, values);
        message.success('Usuário atualizado');
      } else {
        await createUser(values);
        message.success('Usuário criado');
      }
      setDrawerOpen(false);
      setEditing(null);
      await refresh();
    } catch (e: any) {
      if (e?.errorFields) return; // validation
      message.error(e?.message || 'Erro ao salvar');
    }
  }

  async function onDelete(user: User) {
    try {
      await deleteUser(user.id);
      message.success('Usuário excluído');
      await refresh();
    } catch (e: any) {
      message.error(e?.message || 'Erro ao excluir');
    }
  }

  const pagination: TablePaginationConfig = {
    current: page,
    pageSize,
    total,
    showSizeChanger: true,
    pageSizeOptions: [10, 20, 50],
    onChange: (p, ps) => {
      setPage(p);
      setPageSize(ps);
    },
    showTotal: (t) => `${t} itens`,
  };

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: '0 auto' }}>
      <Row align="middle" justify="space-between" style={{ marginBottom: 16 }}>
        <Col>
          <Typography.Title level={3} style={{ margin: 0 }}>
            Usuários
          </Typography.Title>
          <Typography.Text type="secondary">
            Exemplo de CRUD com Table + Drawer + Form
          </Typography.Text>
        </Col>
        <Col>
          <Button type="primary" onClick={openCreate}>
            Novo usuário
          </Button>
        </Col>
      </Row>

      <Card style={{ marginBottom: 16 }}>
        <Form
          form={filtersForm}
          layout="inline"
          initialValues={{ active: 'all' }}
          onFinish={applyFilters}
        >
          <Form.Item name="q">
            <Input placeholder="Buscar por nome ou email" allowClear style={{ width: 260 }} />
          </Form.Item>

          <Form.Item name="role">
            <Select
              placeholder="Role"
              allowClear
              style={{ width: 160 }}
              options={[
                { value: 'admin', label: 'admin' },
                { value: 'user', label: 'user' },
              ]}
            />
          </Form.Item>

          <Form.Item name="active">
            <Select
              style={{ width: 160 }}
              options={[
                { value: 'all', label: 'Todos' },
                { value: true, label: 'Ativos' },
                { value: false, label: 'Inativos' },
              ]}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Filtrar
              </Button>
              <Button onClick={clearFilters}>Limpar</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Card>
        <Table
          rowKey="id"
          loading={loading}
          columns={columns}
          dataSource={items}
          pagination={pagination}
        />
      </Card>

      <Drawer
        title={drawerTitle}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        width={420}
        extra={
          <Space>
            <Button onClick={() => setDrawerOpen(false)}>Cancelar</Button>
            <Button type="primary" onClick={onSave}>
              Salvar
            </Button>
          </Space>
        }
      >
        <Form form={editForm} layout="vertical">
          <Form.Item
            label="Nome"
            name="name"
            rules={[{ required: true, message: 'Informe o nome' }, { min: 2 }]}
          >
            <Input placeholder="Nome" />
          </Form.Item>

          <Form.Item
            label="Email"
            name="email"
            rules={[
              { required: true, message: 'Informe o email' },
              { type: 'email', message: 'Email inválido' },
            ]}
          >
            <Input placeholder="email@exemplo.com" />
          </Form.Item>

          <Row gutter={12}>
            <Col span={12}>
              <Form.Item label="Role" name="role" rules={[{ required: true }]}
              >
                <Select
                  options={[
                    { value: 'admin', label: 'admin' },
                    { value: 'user', label: 'user' },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="Ativo" name="active" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Drawer>
    </div>
  );
}

export default UsersPage;
