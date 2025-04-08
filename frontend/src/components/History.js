import React, { useState, useEffect } from "react";
import { Container, Card, Button, Row, Col } from "react-bootstrap";
import "./History.css";

const History = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/history");
      if (!response.ok) {
        throw new Error("Erreur lors de la récupération de l'historique");
      }
      const data = await response.json();
      setHistory(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = async (requestId) => {
    try {
      const response = await fetch(
        `http://localhost:5000/api/download-pdf/${requestId}`
      );
      if (!response.ok) {
        throw new Error("Erreur lors du téléchargement du PDF");
      }

      // Get the filename from the Content-Disposition header
      const contentDisposition = response.headers.get("Content-Disposition");
      const filename = contentDisposition
        ? contentDisposition.split("filename=")[1].replace(/"/g, "")
        : `contenu_${requestId}.pdf`;

      // Create a blob from the response
      const blob = await response.blob();

      // Create a link element and trigger the download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return <div className="text-center mt-5">Chargement...</div>;
  }

  if (error) {
    return <div className="text-center mt-5 text-danger">{error}</div>;
  }

  return (
    <Container className="mt-4">
      <h2 className="mb-4">Historique des générations</h2>
      {history.length === 0 ? (
        <div className="text-center">Aucun historique disponible</div>
      ) : (
        <Row>
          {history.map((item) => (
            <Col key={item.id} md={6} lg={4} className="mb-4">
              <Card className="h-100">
                <Card.Header>
                  <h5 className="mb-0">{item.subject}</h5>
                  <small className="text-muted">
                    Niveau: {item.grade_level}
                  </small>
                </Card.Header>
                <Card.Body>
                  <Card.Text>
                    <strong>Types de contenu générés:</strong>
                    <ul className="list-unstyled">
                      {item.content_types.map((type, index) => (
                        <li key={index}>• {type}</li>
                      ))}
                    </ul>
                  </Card.Text>
                  <Card.Text>
                    <small className="text-muted">
                      Généré le:{" "}
                      {new Date(item.created_at).toLocaleDateString()}
                    </small>
                  </Card.Text>
                </Card.Body>
                <Card.Footer>
                  <Button
                    variant="primary"
                    onClick={() => downloadPDF(item.id)}
                    className="w-100"
                  >
                    Télécharger en PDF
                  </Button>
                </Card.Footer>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </Container>
  );
};

export default History;
