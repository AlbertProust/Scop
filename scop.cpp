#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <GLFW/glfw3.h>
#include <GL/glu.h>  // Add GLU header for gluPerspective and gluLookAt
#include <cmath>

// Structure minimale pour un sommet (optionnel : ici nous stockons directement les float dans un vecteur)
struct Vertex {
    float x, y, z;
};

// Variables pour la caméra
float cameraX = 0.0f;
float cameraY = 0.0f;
float cameraZ = 5.0f;
float targetX = 0.0f;
float targetY = 0.0f;
float targetZ = 0.0f;
float cameraDistance = 5.0f;  // Distance de la caméra par rapport au centre
float cameraYaw = 0.0f;       // Angle horizontal (en radians)
float cameraPitch = 0.0f;     // Angle vertical (en radians)

// Stockage des sommets et indices des faces (les indices sont supposés former des triangles)
std::vector<Vertex> vertices;
std::vector<unsigned int> indices;

// Callback de gestion des touches clavier
void key_callback(GLFWwindow* window, int key, int scancode, int action, int mods) {
    const float moveSpeed = 0.1f;
    const float rotateSpeed = 0.05f;
    bool targetMoved = false;
    
    if (action == GLFW_PRESS || action == GLFW_REPEAT) {
        // Rotation autour de l'objet (axe Y - gauche/droite)
        if (key == GLFW_KEY_A || key == GLFW_KEY_LEFT)
            cameraYaw += rotateSpeed;
        if (key == GLFW_KEY_D || key == GLFW_KEY_RIGHT)
            cameraYaw -= rotateSpeed;
        
        // Rotation autour de l'objet (axe X - haut/bas)
        if (key == GLFW_KEY_W || key == GLFW_KEY_UP)
            cameraPitch += rotateSpeed;
        if (key == GLFW_KEY_S || key == GLFW_KEY_DOWN)
            cameraPitch -= rotateSpeed;
        
        // Limiter l'angle vertical pour éviter les inversions
        if (cameraPitch > 1.5f) cameraPitch = 1.5f;
        if (cameraPitch < -1.5f) cameraPitch = -1.5f;
        
        // Zoom (ajuster la distance)
        if (key == GLFW_KEY_Q)
            cameraDistance += moveSpeed;
        if (key == GLFW_KEY_E)
            cameraDistance -= moveSpeed;
        
        // Assurer une distance minimale
        if (cameraDistance < 1.0f) cameraDistance = 1.0f;
            
        // Déplacement du point visé (avec les touches I,J,K,L)
        if (key == GLFW_KEY_J) {
            targetX -= moveSpeed;
            targetMoved = true;
        }
        if (key == GLFW_KEY_L) {
            targetX += moveSpeed;
            targetMoved = true;
        }
        if (key == GLFW_KEY_I) {
            targetY += moveSpeed;
            targetMoved = true;
        }
        if (key == GLFW_KEY_K) {
            targetY -= moveSpeed;
            targetMoved = true;
        }
        
        // Calculer la nouvelle position de la caméra en coordonnées sphériques
        cameraX = targetX + cameraDistance * sin(cameraYaw) * cos(cameraPitch);
        cameraY = targetY + cameraDistance * sin(cameraPitch);
        cameraZ = targetZ + cameraDistance * cos(cameraYaw) * cos(cameraPitch);
            
        // Quitter l'application avec Escape
        if (key == GLFW_KEY_ESCAPE)
            glfwSetWindowShouldClose(window, GLFW_TRUE);
    }
}

// Fonction de chargement d'un fichier .obj (prise en charge minimale)
bool loadOBJ(const std::string& filename) {
    std::ifstream inFile(filename);
    if (!inFile) {
        std::cerr << "Erreur : Impossible d'ouvrir le fichier " << filename << std::endl;
        return false;
    }
    
    std::string line;
    while (std::getline(inFile, line)) {
        // Suppression des espaces inutiles
        if (line.substr(0, 2) == "v ") {
            std::istringstream s(line.substr(2));
            Vertex v;
            s >> v.x >> v.y >> v.z;
            vertices.push_back(v);
        } else if (line.substr(0, 2) == "f ") {
            std::istringstream s(line.substr(2));
            unsigned int idx[3];
            // Pour simplifier, on suppose que les faces sont triangulaires et que le format est "f v1 v2 v3".
            // Si le format inclut d'autres informations (normales, textures) il faudra adapter le parsing.
            s >> idx[0] >> idx[1] >> idx[2];
            // Les indices d'un fichier OBJ commencent à 1, on décrémente pour obtenir une indexation à partir de 0.
            indices.push_back(idx[0] - 1);
            indices.push_back(idx[1] - 1);
            indices.push_back(idx[2] - 1);
        }
        // On peut ignorer d'autres types de lignes
    }
    std::cout << "Chargement de " << vertices.size() << " sommets et " 
              << indices.size()/3 << " faces." << std::endl;
    return true;
}

// Affiche les contrôles disponibles
void printControls() {
    std::cout << "Contrôles de la caméra:" << std::endl;
    std::cout << "  Rotation autour de l'objet:" << std::endl;
    std::cout << "    W/Flèche haut    : Rotation vers le haut" << std::endl;
    std::cout << "    S/Flèche bas     : Rotation vers le bas" << std::endl;
    std::cout << "    A/Flèche gauche  : Rotation vers la gauche" << std::endl;
    std::cout << "    D/Flèche droite  : Rotation vers la droite" << std::endl;
    std::cout << "  Zoom:" << std::endl;
    std::cout << "    Q                : S'éloigner" << std::endl;
    std::cout << "    E                : Se rapprocher" << std::endl;
    std::cout << "  Déplacement du centre:" << std::endl;
    std::cout << "    I                : Haut" << std::endl;
    std::cout << "    K                : Bas" << std::endl;
    std::cout << "    J                : Gauche" << std::endl;
    std::cout << "    L                : Droite" << std::endl;
    std::cout << "  Autres:" << std::endl;
    std::cout << "    ESC              : Quitter" << std::endl;
}

void render() {
    // Effacer l'écran
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

   // Always check that our framebuffer is ok
   if(glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
       return false;
    glColor3f(1.0f, 1.0f, 1.0f); // couleur blanche pour le modèle
    
    // Mode immediate pour dessiner les triangles
    glBegin(GL_TRIANGLES);
    for (size_t i = 0; i < indices.size(); i++) {
        Vertex v = vertices[indices[i]];
        glVertex3f(v.x, v.y, v.z);
    }
    glEnd();
}

int main(int ac, char **argv) {

    if (ac != 2) {
        std::cerr << "Erreur : aucun fichier demandé" << std::endl;
        return -1;
    }
    if (!glfwInit()) {
        std::cerr << "Erreur GLFW" << std::endl;
        return -1;
    }
    
    GLFWwindow* window = glfwCreateWindow(1600, 1200, "Modelisation .obj en C++", nullptr, nullptr);
    if (!window) {
        std::cerr << "Erreur : impossible de créer la fenêtre GLFW" << std::endl;
        glfwTerminate();
        return -1;
    }
    glfwMakeContextCurrent(window);
    
    glEnable(GL_DEPTH_TEST);

    cameraDistance = 5.0f;
    cameraYaw = 0.0f;
    cameraPitch = 0.0f;
    cameraX = targetX + cameraDistance * sin(cameraYaw) * cos(cameraPitch);
    cameraY = targetY + cameraDistance * sin(cameraPitch);
    cameraZ = targetZ + cameraDistance * cos(cameraYaw) * cos(cameraPitch);
    
    glfwSetKeyCallback(window, key_callback);

    if (!loadOBJ(argv[1])) {
        std::cerr << "Erreur lors du chargement du modèle." << std::endl;
        glfwTerminate();
        return -1;
    }
    
    // Affichage des contrôles disponibles
    printControls();

    while (!glfwWindowShouldClose(window)) {

        glfwPollEvents();
        
        int width, height;
        glfwGetFramebufferSize(window, &width, &height);
        float ratio = width / (float) height;
        
        glViewport(0, 0, width, height);
        glMatrixMode(GL_PROJECTION);
        glLoadIdentity();
        // Configuration d'une projection perspective simple
        gluPerspective(45.0, ratio, 0.1, 100.0);
        
        glMatrixMode(GL_MODELVIEW);
        glLoadIdentity();
        // Positionnement simple de la caméra
        gluLookAt(cameraX, cameraY, cameraZ,   // position de la caméra
                  targetX, targetY, targetZ,   // point visé
                  0.0, 1.0, 0.0);  // vecteur up

        // Rendu du modèle
        render();
        
        // Échange des buffers pour afficher le rendu
        glfwSwapBuffers(window);
    }
    
    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}
