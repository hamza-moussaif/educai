import React, { useState } from "react";
import { Card, Button, Spinner, Alert, Tabs, Tab } from "react-bootstrap";
import axios from "axios";

const ContentGenerator = ({ formData }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [activeTab, setActiveTab] = useState("qcm");

  const generateContent = async () => {
    setLoading(true);
    setError(null);
    try {
      // Check if at least one content type is selected
      const selectedTypes = Object.entries(formData.contentTypes)
        .filter(([_, value]) => value)
        .map(([key]) => key);

      if (selectedTypes.length === 0) {
        setError("Veuillez sélectionner au moins un type de contenu.");
        return;
      }

      const response = await axios.post(
        "http://localhost:5000/api/generate",
        formData
      );

      // Check if the response contains valid data
      if (!response.data || typeof response.data !== "object") {
        throw new Error("Format de réponse invalide");
      }

      // Parse the content if it's a string
      const content =
        typeof response.data === "string"
          ? JSON.parse(response.data)
          : response.data;

      setGeneratedContent(content);
    } catch (err) {
      console.error("Error details:", err);
      setError(
        err.response?.data?.error ||
          err.message ||
          "Une erreur est survenue lors de la génération du contenu."
      );
    } finally {
      setLoading(false);
    }
  };

  const saveContent = async () => {
    try {
      await axios.post("http://localhost:5000/api/save", {
        content: generatedContent,
        formData: formData,
      });
      alert("Contenu sauvegardé avec succès!");
    } catch (err) {
      setError("Erreur lors de la sauvegarde du contenu.");
      console.error("Error:", err);
    }
  };

  const renderContent = () => {
    if (!generatedContent) return null;

    const contentTypes = Object.keys(generatedContent);
    if (contentTypes.length === 0) {
      return <Alert variant="warning">Aucun contenu généré.</Alert>;
    }

    return (
      <Tabs activeKey={activeTab} onSelect={(k) => setActiveTab(k)}>
        {contentTypes.map((type) => (
          <Tab key={type} eventKey={type} title={getContentTypeTitle(type)}>
            <Card className="mt-3">
              <Card.Body>
                {renderContentByType(type, generatedContent[type])}
              </Card.Body>
            </Card>
          </Tab>
        ))}
      </Tabs>
    );
  };

  const getContentTypeTitle = (type) => {
    const titles = {
      qcm: "QCM",
      exercises: "Exercices",
      fillInTheBlanks: "Textes à trous",
      summary: "Fiches de synthèse",
      conceptMap: "Schémas conceptuels",
    };
    return titles[type] || type;
  };

  const renderContentByType = (type, content) => {
    try {
      // Parse content if it's a string
      const parsedContent =
        typeof content === "string" ? JSON.parse(content) : content;

      switch (type) {
        case "qcm":
          return (
            <div>
              {parsedContent.questions?.map((q, index) => (
                <div key={index} className="mb-4">
                  <h5>Question {index + 1}</h5>
                  <p>{q.question}</p>
                  <ul>
                    {q.options?.map((opt, optIndex) => (
                      <li key={optIndex}>
                        {opt} {optIndex === q.correctAnswer && "✓"}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          );
        case "exercises":
          return (
            <div>
              {parsedContent.exercises?.map((ex, index) => (
                <div key={index} className="mb-4">
                  <h5>Exercice {index + 1}</h5>
                  <p>{ex.statement}</p>
                  <p>
                    <strong>Solution:</strong> {ex.solution}
                  </p>
                </div>
              ))}
            </div>
          );
        case "fillInTheBlanks":
          return (
            <div>
              {parsedContent.texts?.map((text, index) => (
                <div key={index} className="mb-4">
                  <p>{text.text}</p>
                  <p>
                    <strong>Réponses:</strong> {text.answers?.join(", ")}
                  </p>
                </div>
              ))}
            </div>
          );
        case "summary":
          return (
            <div>
              {parsedContent.summaries?.map((sum, index) => (
                <div key={index} className="mb-4">
                  <h5>Synthèse {index + 1}</h5>
                  <p>{sum.content}</p>
                </div>
              ))}
            </div>
          );
        case "conceptMap":
          return (
            <div>
              {parsedContent.maps?.map((map, index) => (
                <div key={index} className="mb-4">
                  <h5>Schéma conceptuel {index + 1}</h5>
                  <p>{map.description}</p>
                </div>
              ))}
            </div>
          );
        default:
          return <p>{JSON.stringify(parsedContent)}</p>;
      }
    } catch (err) {
      console.error("Error rendering content:", err);
      return (
        <Alert variant="danger">Erreur lors de l'affichage du contenu.</Alert>
      );
    }
  };

  return (
    <div>
      {!generatedContent && (
        <Button
          variant="primary"
          onClick={generateContent}
          disabled={loading}
          className="mb-4"
        >
          {loading ? (
            <>
              <Spinner
                as="span"
                animation="border"
                size="sm"
                role="status"
                aria-hidden="true"
                className="me-2"
              />
              Génération en cours...
            </>
          ) : (
            "Générer le Contenu"
          )}
        </Button>
      )}

      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
        </Alert>
      )}

      {generatedContent && (
        <>
          {renderContent()}
          <Button variant="success" onClick={saveContent} className="mt-4">
            Sauvegarder le Contenu
          </Button>
        </>
      )}
    </div>
  );
};

export default ContentGenerator;
