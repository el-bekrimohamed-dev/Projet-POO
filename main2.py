import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

connexion = sqlite3.connect('gestion_taches.db')
curseur = connexion.cursor()

curseur.execute('''
CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL UNIQUE
)
''')

curseur.execute('''
CREATE TABLE IF NOT EXISTS taches (
    id INTEGER PRIMARY KEY,
    titre TEXT NOT NULL,
    description TEXT,
    statut TEXT DEFAULT 'En cours' CHECK (statut IN ('En cours', 'Terminé')),
    priorite TEXT DEFAULT 'Moyenne' CHECK (priorite IN ('Haute', 'Moyenne', 'Basse')),
    utilisateur_id INTEGER,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
)
''')
connexion.commit()

def valider_entree(texte, champ):
    if not texte.strip():
        messagebox.showerror("Erreur", f"Le champ '{champ}' ne peut pas être vide.")
        return False
    return True

def ajouter_utilisateur():
    nom = simpledialog.askstring("Ajouter Utilisateur", "Nom de l'utilisateur :")
    if nom and valider_entree(nom, "Nom"):
        try:
            curseur.execute("INSERT INTO utilisateurs (nom) VALUES (?)", (nom,))
            connexion.commit()
            messagebox.showinfo("Succès", "Utilisateur ajouté avec succès.")
            rafraichir_utilisateurs()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Nom d'utilisateur déjà existant.")

def supprimer_utilisateur():
    id_utilisateur = simpledialog.askinteger("Supprimer Utilisateur", "ID de l'utilisateur :")
    if id_utilisateur:
        curseur.execute("SELECT * FROM utilisateurs WHERE id = ?", (id_utilisateur,))
        utilisateur = curseur.fetchone()
        if utilisateur is None:
            messagebox.showerror("Erreur", f"Aucun utilisateur trouvé avec l'ID {id_utilisateur}.")
            return
        curseur.execute("DELETE FROM utilisateurs WHERE id = ?", (id_utilisateur,))
        connexion.commit()
        messagebox.showinfo("Succès", f"Utilisateur supprimé avec succès.")
        rafraichir_utilisateurs()

def rafraichir_utilisateurs():
    curseur.execute("SELECT id, nom FROM utilisateurs")
    utilisateurs = curseur.fetchall()
    liste_util.delete(0, tk.END)
    combo_utilisateur['values'] = [f"{u[0]} - {u[1]}" for u in utilisateurs]
    for u in utilisateurs:
        liste_util.insert(tk.END, f"ID: {u[0]} | Nom: {u[1]}")

def ajouter_tache():
    if not combo_utilisateur.get():
        messagebox.showerror("Erreur", "Sélectionnez un utilisateur.")
        return
    id_utilisateur = int(combo_utilisateur.get().split(' - ')[0])

    fenetre_ajout = tk.Toplevel(fenetre)
    fenetre_ajout.title("Nouvelle Tâche")
    fenetre_ajout.geometry("400x300")
    fenetre_ajout.configure(bg="#F5F6FA")

    tk.Label(fenetre_ajout, text="Titre :", bg="#F5F6FA", font=("Arial", 11, "bold")).pack(pady=5)
    entree_titre = tk.Entry(fenetre_ajout, width=40)
    entree_titre.pack()

    tk.Label(fenetre_ajout, text="Description :", bg="#F5F6FA", font=("Arial", 11, "bold")).pack(pady=5)
    entree_desc = tk.Entry(fenetre_ajout, width=40)
    entree_desc.pack()

    tk.Label(fenetre_ajout, text="Priorité :", bg="#F5F6FA", font=("Arial", 11, "bold")).pack(pady=5)
    combo_priorite = ttk.Combobox(fenetre_ajout, values=["Haute", "Moyenne", "Basse"], state="readonly", width=38)
    combo_priorite.set("Moyenne")
    combo_priorite.pack()

    def sauvegarder_tache():
        titre = entree_titre.get()
        desc = entree_desc.get()
        prio = combo_priorite.get()
        if valider_entree(titre, "Titre"):
            curseur.execute("INSERT INTO taches (titre, description, priorite, utilisateur_id) VALUES (?, ?, ?, ?)",
                            (titre, desc, prio, id_utilisateur))
            connexion.commit()
            messagebox.showinfo("Succès", "Tâche ajoutée avec succès.")
            rafraichir_taches()
            fenetre_ajout.destroy()

    tk.Button(fenetre_ajout, text="Enregistrer", command=sauvegarder_tache,
              bg="#4A90E2", fg="white", width=15, font=("Arial", 10, "bold")).pack(pady=10)
    tk.Button(fenetre_ajout, text="Annuler", command=fenetre_ajout.destroy,
              bg="#D9534F", fg="white", width=15, font=("Arial", 10, "bold")).pack()

def marquer_termine():
    if not combo_utilisateur.get():
        messagebox.showerror("Erreur", "Sélectionnez un utilisateur.")
        return
    id_utilisateur = int(combo_utilisateur.get().split(' - ')[0])
    id_tache = simpledialog.askinteger("Marquer Terminé", "ID de la tâche :")
    if id_tache:
        curseur.execute("SELECT * FROM taches WHERE id=? AND utilisateur_id=?", (id_tache, id_utilisateur))
        tache = curseur.fetchone()
        if tache is None:
            messagebox.showerror("Erreur", "Aucune tâche trouvée avec cet ID.")
            return
        curseur.execute("UPDATE taches SET statut='Terminé' WHERE id=? AND utilisateur_id=?", (id_tache, id_utilisateur))
        connexion.commit()
        messagebox.showinfo("Succès", "Tâche marquée comme terminée.")
        rafraichir_taches()

def supprimer_tache():
    if not combo_utilisateur.get():
        messagebox.showerror("Erreur", "Sélectionnez un utilisateur.")
        return
    id_utilisateur = int(combo_utilisateur.get().split(' - ')[0])
    id_tache = simpledialog.askinteger("Supprimer Tâche", "ID de la tâche :")
    if id_tache:
        curseur.execute("SELECT * FROM taches WHERE id=? AND utilisateur_id=?", (id_tache, id_utilisateur))
        tache = curseur.fetchone()
        if tache is None:
            messagebox.showerror("Erreur", "Aucune tâche trouvée avec cet ID.")
            return
        curseur.execute("DELETE FROM taches WHERE id=? AND utilisateur_id=?", (id_tache, id_utilisateur))
        connexion.commit()
        messagebox.showinfo("Succès", "Tâche supprimée.")
        rafraichir_taches()

def rafraichir_taches():
    if not combo_utilisateur.get():
        return
    id_utilisateur = int(combo_utilisateur.get().split(' - ')[0])
    curseur.execute("SELECT id, titre, description, priorite, statut FROM taches WHERE utilisateur_id=? ORDER BY id", (id_utilisateur,))
    taches = curseur.fetchall()
    for item in tableau_taches.get_children():
        tableau_taches.delete(item)
    for t in taches:
        tableau_taches.insert("", "end", values=(t[0], t[1], t[2], t[3], t[4]), tags=('noir',))
        tableau_taches.tag_configure('noir', foreground='black')

fenetre = tk.Tk()
fenetre.title("Gestion de Tâches")
fenetre.geometry("950x600")
fenetre.configure(bg="#F5F6FA")

onglets = ttk.Notebook(fenetre)
onglets.pack(fill='both', expand=True, padx=10, pady=10)

onglet_util = ttk.Frame(onglets)
onglets.add(onglet_util, text="Utilisateurs")

cadre_util = ttk.Frame(onglet_util, padding=15)
cadre_util.pack(fill='both', expand=True)
tk.Label(cadre_util, text="Gestion des Utilisateurs", font=("Arial", 16, "bold"), fg="#4A90E2").pack(pady=20)
cadre_boutons_util = tk.Frame(cadre_util, bg="#F5F6FA")
cadre_boutons_util.pack(pady=20)
tk.Button(cadre_boutons_util, text="Ajouter Utilisateur", command=ajouter_utilisateur,
          bg="#4A90E2", fg="white", width=20, height=2, font=("Arial", 12, "bold")).pack(pady=10)
tk.Button(cadre_boutons_util, text="Supprimer Utilisateur", command=supprimer_utilisateur,
          bg="#D9534F", fg="white", width=20, height=2, font=("Arial", 12, "bold")).pack(pady=10)
liste_util = tk.Listbox(cadre_util, height=15, width=70, font=("Arial", 10))
liste_util.pack(pady=20)

onglet_taches = ttk.Frame(onglets)
onglets.add(onglet_taches, text="Tâches")

cadre_tache = ttk.Frame(onglet_taches, padding=15)
cadre_tache.pack(fill='both', expand=True)

tk.Label(cadre_tache, text="Sélectionnez un utilisateur :", font=("Arial", 12, "bold"), fg="#4A90E2").pack()
combo_utilisateur = ttk.Combobox(cadre_tache, state="readonly", width=50, font=("Arial", 10))
combo_utilisateur.pack(pady=10)
combo_utilisateur.bind("<<ComboboxSelected>>", lambda e: rafraichir_taches())

frame_btn = tk.Frame(cadre_tache, bg="#F5F6FA")
frame_btn.pack(pady=15)
tk.Button(frame_btn, text="Ajouter Tâche", command=ajouter_tache,
          bg="#4A90E2", fg="white", width=15, font=("Arial", 10, "bold")).pack(side='left', padx=8)
tk.Button(frame_btn, text="Marquer Terminé", command=marquer_termine,
          bg="#F0AD4E", fg="white", width=15, font=("Arial", 10, "bold")).pack(side='left', padx=8)
tk.Button(frame_btn, text="Supprimer Tâche", command=supprimer_tache,
          bg="#D9534F", fg="white", width=15, font=("Arial", 10, "bold")).pack(side='left', padx=8)

colonnes = ("ID", "Tâche", "Description", "Priorité", "Statut")
tableau_taches = ttk.Treeview(cadre_tache, columns=colonnes, show="headings", height=18)
for col in colonnes:
    tableau_taches.heading(col, text=col)
    tableau_taches.column(col, width=170 if col != "Description" else 250, anchor="center")
tableau_taches.pack(fill="both", expand=True, pady=10)

tk.Button(fenetre, text="Quitter", command=fenetre.quit,
          bg="#6C757D", fg="white", width=15, font=("Arial", 10, "bold")).pack(pady=10)

rafraichir_utilisateurs()
fenetre.mainloop()
connexion.close()
