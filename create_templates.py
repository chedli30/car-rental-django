#!/usr/bin/env python
"""Create all modern template files for AutoLux"""

templates = {
    'login.html': '''{% extends "base.html" %}

{% block title %}Connexion - AutoLux{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center align-items-center" style="min-height: 70vh;">
        <div class="col-md-6 col-lg-5">
            <div class="card">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <div style="width: 60px; height: 60px; border-radius: 12px; background: #EBF2F9; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; color: #1A56DB; font-size: 2rem;">
                            <i class="fas fa-sign-in-alt"></i>
                        </div>
                        <h2 style="margin-bottom: 0.5rem;">Connexion</h2>
                        <p class="text-secondary">Accédez à votre compte AutoLux</p>
                    </div>

                    {% if messages %}
                        {% for message in messages %}
                        <div class="alert alert-{{ message.tags }}" role="alert">
                            {{ message }}
                        </div>
                        {% endfor %}
                    {% endif %}

                    <form method="POST">
                        {% csrf_token %}
                        <div class="form-group mb-3">
                            <label class="form-label">Nom d'utilisateur</label>
                            <input type="text" name="username" class="form-control" required autofocus>
                        </div>

                        <div class="form-group mb-4">
                            <label class="form-label">Mot de passe</label>
                            <input type="password" name="password" class="form-control" required>
                        </div>

                        <div class="form-check mb-4">
                            <input type="checkbox" name="remember" id="remember" class="form-check-input">
                            <label class="form-check-label" for="remember">Se souvenir de moi</label>
                        </div>

                        <button type="submit" class="btn btn-primary btn-block mb-3">
                            <i class="fas fa-sign-in-alt"></i> Connexion
                        </button>
                    </form>

                    <div class="text-center pt-3 border-top">
                        <p class="text-secondary mb-0">
                            Pas encore de compte ?
                            <a href="/rentals/register/" class="text-accent fw-600">S'inscrire</a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',

    'register.html': '''{% extends "base.html" %}

{% block title %}Inscription - AutoLux{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center align-items-center" style="min-height: 70vh;">
        <div class="col-md-6 col-lg-5">
            <div class="card">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <div style="width: 60px; height: 60px; border-radius: 12px; background: #EBF2F9; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; color: #1A56DB; font-size: 2rem;">
                            <i class="fas fa-user-plus"></i>
                        </div>
                        <h2 style="margin-bottom: 0.5rem;">Créer un compte</h2>
                        <p class="text-secondary">Rejoignez AutoLux en 2 minutes</p>
                    </div>

                    {% if messages %}
                        {% for message in messages %}
                        <div class="alert alert-{{ message.tags }}" role="alert">
                            {{ message }}
                        </div>
                        {% endfor %}
                    {% endif %}

                    <form method="POST">
                        {% csrf_token %}
                        <div class="form-group mb-3">
                            <label class="form-label">Nom d'utilisateur</label>
                            <input type="text" name="username" class="form-control" required>
                        </div>

                        <div class="form-group mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" name="email" class="form-control" required>
                        </div>

                        <div class="form-group mb-3">
                            <label class="form-label">Mot de passe</label>
                            <input type="password" name="password1" class="form-control" required>
                        </div>

                        <div class="form-group mb-4">
                            <label class="form-label">Confirmer le mot de passe</label>
                            <input type="password" name="password2" class="form-control" required>
                        </div>

                        <div class="form-group mb-4">
                            <label class="form-label">Rôle</label>
                            <select name="role" class="form-select" required>
                                <option value="user">👤 Utilisateur</option>
                                <option value="admin">🔧 Administrateur (requiert approbation)</option>
                            </select>
                        </div>

                        <button type="submit" class="btn btn-primary btn-block mb-3">
                            <i class="fas fa-check"></i> Créer mon compte
                        </button>
                    </form>

                    <div class="text-center pt-3 border-top">
                        <p class="text-secondary mb-0">
                            Déjà un compte ?
                            <a href="/login/" class="text-accent fw-600">Se connecter</a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',

    'about.html': '''{% extends "base.html" %}

{% block title %}À propos - AutoLux{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row mb-5">
        <div class="col-lg-8 mx-auto text-center">
            <h1>À propos de AutoLux</h1>
            <p class="lead text-secondary">Votre partenaire de confiance pour la location de véhicules premium en Tunisie depuis 2015.</p>
        </div>
    </div>

    <div class="row align-items-center mb-5" style="gap: 2rem;">
        <div class="col-md-6">
            <h3>Notre Histoire</h3>
            <p>Fondée en 2015, AutoLux a commencé comme une petite agence de location de voitures à Tunis. Grâce à notre engagement envers la qualité et le service client, nous avons grandi pour devenir l'une des plus grandes plateformes de location de véhicules en Tunisie.</p>
            <p>Aujourd'hui, nous servons des milliers de clients satisfaits chaque année, du tourisme aux déplacements professionnels.</p>
        </div>
        <div class="col-md-6">
            <div class="card" style="background: linear-gradient(135deg, #EBF2F9, #F3F4F6);">
                <div class="card-body p-5 text-center">
                    <h3 class="text-accent">5000+</h3>
                    <p class="text-secondary">Clients satisfaits</p>
                    <hr>
                    <h3 class="text-accent">500+</h3>
                    <p class="text-secondary">Véhicules dans notre flotte</p>
                </div>
            </div>
        </div>
    </div>

    <div class="row mb-5">
        <div class="col-md-4">
            <div class="text-center">
                <div style="width: 60px; height: 60px; border-radius: 12px; background: #EBF2F9; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; color: #1A56DB; font-size: 2rem;">
                    <i class="fas fa-target"></i>
                </div>
                <h5>Notre Mission</h5>
                <p class="text-secondary">Offrir une expérience de location de voitures simple, transparente et abordable.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="text-center">
                <div style="width: 60px; height: 60px; border-radius: 12px; background: #EBF2F9; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; color: #1A56DB; font-size: 2rem;">
                    <i class="fas fa-eye"></i>
                </div>
                <h5>Notre Vision</h5>
                <p class="text-secondary">Révolutionner la location de voitures en Tunisie avec la technologie et l'innovation.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="text-center">
                <div style="width: 60px; height: 60px; border-radius: 12px; background: #EBF2F9; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; color: #1A56DB; font-size: 2rem;">
                    <i class="fas fa-heart"></i>
                </div>
                <h5>Nos Valeurs</h5>
                <p class="text-secondary">Intégrité, excellence, engagement envers nos clients et communautés.</p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',

    'contact.html': '''{% extends "base.html" %}

{% block title %}Contact - AutoLux{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row mb-5">
        <div class="col-lg-8 mx-auto text-center">
            <h1>Nous contacter</h1>
            <p class="lead text-secondary">Des questions ? Notre équipe est disponible pour vous aider.</p>
        </div>
    </div>

    <div class="row g-4 mb-5">
        <div class="col-md-4">
            <div class="card text-center">
                <div class="card-body">
                    <div style="width: 60px; height: 60px; border-radius: 12px; background: #EBF2F9; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; color: #1A56DB; font-size: 2rem;">
                        <i class="fas fa-map-marker-alt"></i>
                    </div>
                    <h5>Adresse</h5>
                    <p class="text-secondary">Rue Mohamed Ali<br>Tunis, Tunisie</p>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card text-center">
                <div class="card-body">
                    <div style="width: 60px; height: 60px; border-radius: 12px; background: #EBF2F9; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; color: #1A56DB; font-size: 2rem;">
                        <i class="fas fa-phone"></i>
                    </div>
                    <h5>Téléphone</h5>
                    <p class="text-secondary"><a href="tel:+21671000000" style="color: #1A56DB;">+216 71 000 000</a></p>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card text-center">
                <div class="card-body">
                    <div style="width: 60px; height: 60px; border-radius: 12px; background: #EBF2F9; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; color: #1A56DB; font-size: 2rem;">
                        <i class="fas fa-envelope"></i>
                    </div>
                    <h5>Email</h5>
                    <p class="text-secondary"><a href="mailto:info@autolux.tn" style="color: #1A56DB;">info@autolux.tn</a></p>
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-lg-8 mx-auto">
            <div class="card">
                <div class="card-body p-5">
                    <h4 class="mb-4">Envoyez-nous un message</h4>
                    <form method="POST" action="/rentals/support/">
                        {% csrf_token %}
                        <div class="form-group mb-3">
                            <label class="form-label">Nom</label>
                            <input type="text" name="name" class="form-control" required>
                        </div>

                        <div class="form-group mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" name="email" class="form-control" required>
                        </div>

                        <div class="form-group mb-3">
                            <label class="form-label">Sujet</label>
                            <input type="text" name="subject" class="form-control" required>
                        </div>

                        <div class="form-group mb-4">
                            <label class="form-label">Message</label>
                            <textarea name="message" class="form-control" rows="5" required></textarea>
                        </div>

                        <button type="submit" class="btn btn-primary btn-lg">
                            <i class="fas fa-paper-plane"></i> Envoyer
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',

    'payments.html': '''{% extends "base.html" %}

{% block title %}Paiements - AutoLux{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="mb-4">
        <h1>Gestion des paiements</h1>
        <p class="text-secondary">Consultez et gérez vos paiements</p>
    </div>

    <div class="card">
        <div class="card-header">
            <h5 class="mb-0">Historique des paiements</h5>
        </div>
        <div class="card-body">
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Montant</th>
                            <th>Statut</th>
                            <th>Méthode</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>01/04/2026</td>
                            <td>450 DT</td>
                            <td><span class="badge badge-success">Payé</span></td>
                            <td>Carte bancaire</td>
                            <td><a href="#" class="btn btn-sm btn-secondary">Détails</a></td>
                        </tr>
                        <tr>
                            <td>28/03/2026</td>
                            <td>300 DT</td>
                            <td><span class="badge badge-success">Payé</span></td>
                            <td>Virement</td>
                            <td><a href="#" class="btn btn-sm btn-secondary">Détails</a></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
}

import os
base_path = '/'.join(__file__.split('/')[:-1])

for filename, content in templates.items():
    filepath = os.path.join(base_path, 'templates', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created {filename}")

print(f"\\n✅ All {len(templates)} template files created successfully!")
