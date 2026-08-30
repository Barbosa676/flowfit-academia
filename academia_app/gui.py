import tkinter as tk
from tkinter import ttk, messagebox
from . import db


class GymApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('FlowFit | Gestão de Clientes')
        self.geometry('1100x620')
        self.minsize(980, 540)
        self.configure(bg='#0b1120')

        self._apply_theme()
        db.init_db()

        if not db.get_plans():
            db.add_plan('Mensal', 100.0)
            db.add_plan('Trimestral', 270.0)
            db.add_plan('Anual', 1000.0)

        self.create_widgets()
        self.refresh_clients()

    def _apply_theme(self):
        style = ttk.Style(self)
        style.theme_use('clam')

        bg_dark = '#0a0f1a'
        bg_panel = '#101926'
        bg_soft = '#141f2d'
        bg_input = '#0e1726'
        text_primary = '#f5f7fb'
        text_muted = '#b7c4d8'
        gold = '#d4af37'
        gold_soft = '#f7d77a'
        emerald = '#8be9b0'
        emerald_dark = '#3ecf8e'
        red = '#ff6b6b'
        border = '#1f2d3d'

        style.configure('Main.TFrame', background=bg_dark)
        style.configure('Sidebar.TFrame', background=bg_panel)
        style.configure('Panel.TFrame', background=bg_panel)
        style.configure('Header.TLabel', background=bg_dark, foreground=text_primary, font=('Segoe UI', 25, 'bold'))
        style.configure('SubHeader.TLabel', background=bg_dark, foreground=text_muted, font=('Segoe UI', 10, 'normal'))
        style.configure('Label.TLabel', background=bg_panel, foreground='#f8fafc', font=('Segoe UI', 10, 'bold'))
        style.configure('Field.TEntry', fieldbackground=bg_input, foreground=text_primary, insertcolor=text_primary)
        style.configure('Treeview', background=bg_input, foreground=text_primary, rowheight=32, fieldbackground=bg_input)
        style.map('Treeview', background=[('selected', emerald_dark)], foreground=[('selected', '#062d1d')])
        style.configure('Treeview.Heading', background='#1c2a3d', foreground=text_primary, font=('Segoe UI', 10, 'bold'))
        style.map('Treeview.Heading', background=[('active', '#24344d')])

    def create_widgets(self):
        root = ttk.Frame(self, style='Main.TFrame')
        root.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        header = ttk.Frame(root, style='Main.TFrame')
        header.pack(fill=tk.X, pady=(0, 18))

        ttk.Label(header, text='FlowFit', style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(header, text='Sistema de gestão de clientes da academia', style='SubHeader.TLabel').pack(anchor=tk.W, pady=(4, 0))

        content = ttk.Frame(root, style='Main.TFrame')
        content.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(content, style='Sidebar.TFrame', padding=18)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 18))
        left.configure(width=300)

        ttk.Label(left, text='Novo cliente', style='Label.TLabel').pack(anchor=tk.W, pady=(0, 12))

        def create_field(parent, label_text, icon):
            frame = tk.Frame(parent, bg='#142236', bd=1, relief='flat', highlightbackground='#26344a', highlightthickness=1)
            frame.pack(fill=tk.X, pady=(0, 8))

            label = tk.Label(frame, text=f'{icon} {label_text}', bg='#142236', fg='#e6edf8', font=('Segoe UI', 10, 'bold'))
            label.pack(anchor=tk.W, padx=10, pady=(8, 4))

            entry = tk.Entry(frame, width=28, bg='#0d1727', fg='#f8fafc', insertbackground='#f8fafc', bd=0, relief='flat')
            entry.pack(fill=tk.X, padx=10, pady=(0, 10))
            return entry

        self.name_entry = create_field(left, 'Nome', '👤')
        self.email_entry = create_field(left, 'Email', '✉')
        self.phone_entry = create_field(left, 'Telefone', '📞')
        self.name_entry.bind('<Return>', lambda event: self.add_client())
        self.email_entry.bind('<Return>', lambda event: self.add_client())
        self.phone_entry.bind('<Return>', lambda event: self.add_client())

        def glass_button(parent, text, bg, fg, command=None):
            btn = tk.Button(
                parent,
                text=text,
                bg=bg,
                fg=fg,
                activebackground=bg,
                activeforeground=fg,
                highlightthickness=0,
                bd=0,
                relief='flat',
                padx=16,
                pady=11,
                font=('Segoe UI', 10, 'bold'),
                command=command,
                cursor='hand2'
            )
            btn.configure(
                highlightbackground=bg,
                highlightcolor=bg,
            )
            return btn

        btn_add = glass_button(left, 'Adicionar cliente', '#8be9b0', '#062d1d', self.add_client)
        btn_add.pack(fill=tk.X, pady=(0, 8))

        btn_edit = glass_button(left, 'Editar selecionado', '#d4af37', '#1a1308', self.edit_selected)
        btn_edit.pack(fill=tk.X, pady=(0, 8))

        btn_del = glass_button(left, 'Excluir selecionado', '#ff6b6b', '#fff5f5', self.delete_selected)
        btn_del.pack(fill=tk.X)

        right = ttk.Frame(content, style='Panel.TFrame', padding=18)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(right, text='Clientes cadastrados', style='Label.TLabel').pack(anchor=tk.W, pady=(0, 12))

        cols = ('id', 'name', 'email', 'phone')
        self.tree = ttk.Treeview(right, columns=cols, show='headings', selectmode='browse')
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Nome')
        self.tree.heading('email', text='Email')
        self.tree.heading('phone', text='Telefone')
        self.tree.column('id', width=60, anchor=tk.CENTER)
        self.tree.column('name', width=220, anchor=tk.W)
        self.tree.column('email', width=250, anchor=tk.W)
        self.tree.column('phone', width=170, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def add_client(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning('Aviso', 'Nome obrigatório')
            self.name_entry.focus_set()
            return

        email = self.email_entry.get().strip() or None
        phone = self.phone_entry.get().strip() or None
        db.add_client(name, email, phone)

        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.refresh_clients()
        self.name_entry.focus_set()
        messagebox.showinfo('Sucesso', f'Cliente "{name}" cadastrado com sucesso!')

    def refresh_clients(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        rows = db.get_clients()
        for row in rows:
            self.tree.insert('', tk.END, values=(row['id'], row['name'], row['email'] or '', row['phone'] or ''))

    def selected_client_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        item = self.tree.item(sel[0])
        return item['values'][0]

    def edit_selected(self):
        cid = self.selected_client_id()
        if cid is None:
            messagebox.showinfo('Info', 'Selecione um cliente')
            return

        row = db.get_client(cid)
        if not row:
            messagebox.showerror('Erro', 'Cliente não encontrado')
            return

        def on_ok():
            name = name_e.get().strip()
            email = email_e.get().strip() or None
            phone = phone_e.get().strip() or None
            if not name:
                messagebox.showwarning('Aviso', 'Nome obrigatório')
                return

            db.update_client(cid, name, email, phone)
            top.destroy()
            self.refresh_clients()

        top = tk.Toplevel(self)
        top.title('Editar cliente')
        top.configure(bg='#101926')

        frame = tk.Frame(top, bg='#101926', padx=18, pady=18)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text='Nome', bg='#101926', fg='#f3f4f6', font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        name_e = tk.Entry(frame, bg='#0d1727', fg='#f8fafc', insertbackground='#f8fafc', width=30)
        name_e.pack(fill=tk.X, pady=(0, 10))
        name_e.insert(0, row['name'])

        tk.Label(frame, text='Email', bg='#101926', fg='#f3f4f6', font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        email_e = tk.Entry(frame, bg='#0d1727', fg='#f8fafc', insertbackground='#f8fafc', width=30)
        email_e.pack(fill=tk.X, pady=(0, 10))
        email_e.insert(0, row['email'] or '')

        tk.Label(frame, text='Telefone', bg='#101926', fg='#f3f4f6', font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        phone_e = tk.Entry(frame, bg='#0d1727', fg='#f8fafc', insertbackground='#f8fafc', width=30)
        phone_e.pack(fill=tk.X, pady=(0, 16))
        phone_e.insert(0, row['phone'] or '')

        save_btn = tk.Button(
            frame,
            text='Salvar alterações',
            bg='#d4af37',
            fg='#1a1308',
            activebackground='#f7d77a',
            activeforeground='#1a1308',
            highlightthickness=0,
            bd=0,
            relief='flat',
            padx=16,
            pady=10,
            font=('Segoe UI', 10, 'bold'),
            command=on_ok,
            cursor='hand2'
        )
        save_btn.pack(fill=tk.X)

    def delete_selected(self):
        cid = self.selected_client_id()
        if cid is None:
            messagebox.showinfo('Info', 'Selecione um cliente na tabela')
            return

        cliente = db.get_client(cid)
        nome = cliente['name'] if cliente else 'este cliente'

        if messagebox.askyesno('Confirma', f'Excluir {nome} do cadastro?'):
            db.delete_client(cid)
            self.refresh_clients()
            messagebox.showinfo('Sucesso', f'{nome} foi removido com sucesso!')
