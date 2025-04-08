import React, { useState } from "react";
import { Form, Card, Row, Col, Button, Alert } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import "./SubjectInputForm.css";

const SubjectInputForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    subject: "",
    gradeLevel: "",
    contentTypes: {
      qcm: false,
      exercises: false,
      fillInTheBlanks: false,
      summary: false,
      conceptMap: false,
    },
    difficulty: 5,
    quantity: 3, // Réduit la quantité par défaut
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showWarning, setShowWarning] = useState(false);

  const validateForm = () => {
    const newErrors = {};
    if (!formData.subject.trim()) {
      newErrors.subject = "Le sujet est requis";
    }
    if (!formData.gradeLevel) {
      newErrors.gradeLevel = "Le niveau scolaire est requis";
    }
    if (!Object.values(formData.contentTypes).some((value) => value)) {
      newErrors.contentTypes = "Sélectionnez au moins un type de contenu";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (type === "checkbox") {
      setFormData((prev) => ({
        ...prev,
        contentTypes: {
          ...prev.contentTypes,
          [name]: checked,
        },
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
    // Clear error when user makes changes
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      // Vérifier le nombre de types de contenu sélectionnés
      const selectedTypes = Object.values(formData.contentTypes).filter(
        Boolean
      ).length;
      const totalItems = selectedTypes * formData.quantity;

      if (totalItems > 5) {
        setShowWarning(true);
        return;
      }

      setIsSubmitting(true);
      onSubmit(formData);
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="mb-4 shadow-sm">
      <Card.Header className="bg-primary text-white">
        <h3 className="mb-0">Générer du Contenu Pédagogique</h3>
      </Card.Header>
      <Card.Body>
        <Form onSubmit={handleSubmit}>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Sujet</Form.Label>
                <Form.Control
                  type="text"
                  name="subject"
                  value={formData.subject}
                  onChange={handleInputChange}
                  placeholder="Entrez le sujet"
                  className={errors.subject ? "is-invalid" : ""}
                />
                {errors.subject && (
                  <Form.Control.Feedback type="invalid">
                    {errors.subject}
                  </Form.Control.Feedback>
                )}
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Niveau Scolaire</Form.Label>
                <Form.Select
                  name="gradeLevel"
                  value={formData.gradeLevel}
                  onChange={handleInputChange}
                  className={errors.gradeLevel ? "is-invalid" : ""}
                >
                  <option value="">Sélectionnez un niveau</option>
                  <option value="primaire">Primaire</option>
                  <option value="college">Collège</option>
                  <option value="lycee">Lycée</option>
                  <option value="superieur">Supérieur</option>
                </Form.Select>
                {errors.gradeLevel && (
                  <Form.Control.Feedback type="invalid">
                    {errors.gradeLevel}
                  </Form.Control.Feedback>
                )}
              </Form.Group>
            </Col>
          </Row>

          <Form.Group className="mb-3">
            <Form.Label>Types de Contenu</Form.Label>
            <div className="content-types-grid">
              <Form.Check
                type="checkbox"
                name="qcm"
                label="QCM"
                checked={formData.contentTypes.qcm}
                onChange={handleInputChange}
                className="content-type-check"
              />
              <Form.Check
                type="checkbox"
                name="exercises"
                label="Exercices"
                checked={formData.contentTypes.exercises}
                onChange={handleInputChange}
                className="content-type-check"
              />
              <Form.Check
                type="checkbox"
                name="fillInTheBlanks"
                label="Textes à trous"
                checked={formData.contentTypes.fillInTheBlanks}
                onChange={handleInputChange}
                className="content-type-check"
              />
              <Form.Check
                type="checkbox"
                name="summary"
                label="Fiches de synthèse"
                checked={formData.contentTypes.summary}
                onChange={handleInputChange}
                className="content-type-check"
              />
              <Form.Check
                type="checkbox"
                name="conceptMap"
                label="Schémas conceptuels"
                checked={formData.contentTypes.conceptMap}
                onChange={handleInputChange}
                className="content-type-check"
              />
            </div>
            {errors.contentTypes && (
              <Alert variant="danger" className="mt-2">
                {errors.contentTypes}
              </Alert>
            )}
          </Form.Group>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Difficulté: {formData.difficulty}</Form.Label>
                <Form.Range
                  name="difficulty"
                  min="1"
                  max="10"
                  value={formData.difficulty}
                  onChange={handleInputChange}
                  className="custom-range"
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Quantité: {formData.quantity}</Form.Label>
                <Form.Range
                  name="quantity"
                  min="1"
                  max="5"
                  value={formData.quantity}
                  onChange={handleInputChange}
                  className="custom-range"
                />
                <small className="text-muted">
                  Maximum 5 éléments par type de contenu
                </small>
              </Form.Group>
            </Col>
          </Row>

          {showWarning && (
            <Alert variant="warning" className="mb-3">
              <strong>Attention :</strong> Pour la version gratuite, veuillez
              limiter votre demande à 5 éléments au total (nombre de types ×
              quantité).
            </Alert>
          )}

          <Button
            variant="primary"
            type="submit"
            className="w-100"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Génération en cours..." : "Générer le Contenu"}
          </Button>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default SubjectInputForm;
