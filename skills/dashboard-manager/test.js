const dashboardSkill = require("./index.js");

dashboardSkill.init().then(success => {
    if (success) {
        console.log("🚀 Dashboard Manager skill initialisé avec succès!");
        
        // Test des fonctions principales
        testFunctions();
    } else {
        console.log("❌ Échec de l'initialisation du skill");
    }
});

async function testFunctions() {
    console.log("🧪 Test des fonctions du Dashboard Manager...");
    
    try {
        // Test 1: Charger la base de données
        console.log("📄 1. Test de chargement de la base de données...");
        const db = await dashboardSkill.loadDatabase();
        console.log("✅ Base de données chargée avec succès");
        console.log("📋 Contenu:", JSON.stringify(db, null, 2));
        
        // Test 2: Récupérer les notes pending
        console.log("📩 2. Test de récupération des notes pending...");
        const pendingNotes = await dashboardSkill.getPendingNotes();
        console.log("✅ Notes récupérées:", pendingNotes);
        
        // Test 3: Ajouter un log
        console.log("📝 3. Test d'ajout d'un log...");
        await dashboardSkill.addLog("🧪 Test du Dashboard Manager skill");
        console.log("✅ Log ajouté avec succès");
        
        // Test 4: Mettre à jour le statut du système
        console.log("⚡ 4. Test de mise à jour du statut du système...");
        await dashboardSkill.updateSystemStatus("🔄 working", "Claude-3-Opus");
        console.log("✅ Statut mis à jour avec succès");
        
        // Test 5: Mettre à jour les statistiques
        console.log("💰 5. Test de mise à jour des statistiques...");
        await dashboardSkill.updateStats(1000, 1500, 0.25);
        console.log("✅ Statistiques mises à jour avec succès");
        
        // Test 6: Ajouter une tâche
        console.log("✅ 6. Test d'ajout d'une tâche...");
        await dashboardSkill.updateTask(null, {
            text: "Test de la création d'une tâche",
            status: "todo",
            priority: "medium",
            tag: "Test"
        });
        console.log("✅ Tâche ajoutée avec succès");
        
        // Test 7: Ajouter un sub-agent
        console.log("🤖 7. Test d'ajout d'un sub-agent...");
        await dashboardSkill.addSubAgent("test_agent", "Test du skill");
        console.log("✅ Sub-agent ajouté avec succès");
        
        // Test 8: Retirer le sub-agent
        console.log("🔴 8. Test de retrait d'un sub-agent...");
        await dashboardSkill.removeSubAgent("test_agent");
        console.log("✅ Sub-agent retiré avec succès");
        
        console.log("🎉 Tous les tests sont passés avec succès!");
        
    } catch (error) {
        console.error("❌ Erreur lors des tests:", error);
    }
}