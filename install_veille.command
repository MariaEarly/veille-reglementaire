#!/bin/zsh
# ============================================================
# Veille Réglementaire — Installation
# Double-cliquez pour installer :
#   1. Lancement automatique au démarrage du Mac
#   2. Application "Veille" dans le Dock
# ============================================================

set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=============================="
echo " Installation Veille Réglementaire"
echo "=============================="
echo ""

# --- 1. Installer feedparser ---
echo "[1/4] Vérification de feedparser..."
if ! python3 -c "import feedparser" 2>/dev/null; then
  echo "  Installation de feedparser..."
  pip3 install feedparser --break-system-packages 2>/dev/null || pip3 install feedparser
  echo "  ✓ feedparser installé"
else
  echo "  ✓ feedparser déjà installé"
fi

# --- 2. LaunchAgent (démarrage auto) ---
echo "[2/4] Configuration du lancement automatique..."
PLIST_SRC="$DIR/com.veille.server.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.veille.server.plist"

# Stopper l'ancien agent s'il existe
launchctl unload "$PLIST_DST" 2>/dev/null || true

# Créer le dossier LaunchAgents si nécessaire
mkdir -p "$HOME/Library/LaunchAgents"

# Copier et personnaliser le plist avec le bon chemin
sed "s|__VEILLE_DIR__|$DIR|g" "$PLIST_SRC" > "$PLIST_DST"

# Charger l'agent
launchctl load "$PLIST_DST"
echo "  ✓ Le serveur se lancera automatiquement au démarrage"

# --- 3. Créer l'application pour le Dock ---
echo "[3/4] Création de l'application Veille..."
APP_DIR="$HOME/Applications/Veille.app"
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Script principal de l'app
cat > "$APP_DIR/Contents/MacOS/Veille" << 'APPSCRIPT'
#!/bin/zsh
open "http://127.0.0.1:8001"
APPSCRIPT
chmod +x "$APP_DIR/Contents/MacOS/Veille"

# Info.plist de l'app
cat > "$APP_DIR/Contents/Info.plist" << 'INFOPLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Veille</string>
    <key>CFBundleDisplayName</key>
    <string>Veille Réglementaire</string>
    <key>CFBundleIdentifier</key>
    <string>com.veille.app</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>Veille</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>
INFOPLIST

echo "  ✓ Application créée dans $APP_DIR"

# --- 4. Vérifier que le serveur tourne ---
echo "[4/4] Vérification du serveur..."
sleep 2
if curl -sf "http://127.0.0.1:8001/" >/dev/null 2>&1; then
  echo "  ✓ Serveur actif sur http://127.0.0.1:8001"
else
  echo "  ⚠ Le serveur n'est pas encore prêt. Il démarrera au prochain redémarrage."
fi

echo ""
echo "=============================="
echo " Installation terminée !"
echo "=============================="
echo ""
echo " • Le serveur se lance automatiquement au démarrage du Mac"
echo " • Pour ajouter au Dock : ouvre le Finder, va dans ~/Applications,"
echo "   puis glisse 'Veille' dans ta barre du Dock"
echo " • Ou tape dans le Terminal :"
echo "   open $APP_DIR"
echo ""
echo " Tu peux fermer cette fenêtre."
