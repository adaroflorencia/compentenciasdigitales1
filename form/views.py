from django.shortcuts import render, get_object_or_404, redirect
from .models import Role, Topic, Question, Option, TopicResult, Answer
import uuid
import logging
from pdf_generator.views import generar_pdf


def docente(request):
    request.session.flush()
    request.session['role_id'] = 3
    return render(request, 'form/docentes.html', {'role_id': request.session.get('role_id')})


def estudiante(request):
    request.session.flush()
    request.session['role_id'] = 2
    return render(request, 'form/estudiantes.html', {'role_id': request.session.get('role_id')})


def no_docentes(request):
    request.session.flush()
    request.session['role_id'] = 4
    return render(request, 'form/no_docentes.html', {'role_id': request.session.get('role_id')})


def generate_form(request, role_id):
    try:
        # Guardar el rol en la sesión para usarlo más tarde
        request.session['role_id'] = role_id

        # Buscar el rol en la base de datos
        role = get_object_or_404(Role, id=role_id)

        logging.info(f"Role instance: {role}")

        # Obtener tópicos y preguntas según el rol
        topics = Topic.objects.filter(role=role)
        questions = Question.objects.filter(topic__in=topics)

        request.session['questions'] = [q.id for q in questions]

        # Crear un ID de sesión único si no existe
        if 'session_id' not in request.session:
            uuid_str = str(uuid.uuid4()).replace('-', '')[:32]
            request.session['session_id'] = uuid_str

        # Guardar preguntas en la sesión para evaluación
        request.session['all_questions'] = [q.id for q in questions]
        request.session['current_question'] = 0
        request.session['answers'] = {}
        request.session['topic_scores'] = {}
        request.session['question_scores'] = {}
        request.session.modified = True

        return redirect('evaluate', role_id=role.id)

    except Exception as e:
        logging.error(f"Error generando formulario para el rol {role_id}: {e}")
        return render(request, 'form/error.html', {'message': 'Error generando el formulario.'})


def evaluate(request, role_id):
    # Recuperar preguntas de la sesión
    question_ids = request.session.get('all_questions', [])
    all_questions = Question.objects.filter(id__in=question_ids)

    # Obtener el rol por su ID
    role = get_object_or_404(Role, id=role_id)

    if not all_questions.exists():
        return redirect('generate_form', role_id=role_id)

    # Inicializar variables de sesión
    if 'answers' not in request.session:
        request.session['answers'] = {}
    if 'current_question' not in request.session:
        request.session['current_question'] = 0
    if 'topic_scores' not in request.session:
        request.session['topic_scores'] = {}
    if 'question_scores' not in request.session:
        request.session['question_scores'] = {}

    # Obtener el ID de sesión
    session_id = request.session.get('session_id')
    if not session_id:
        request.session['session_id'] = str(uuid.uuid4())
        session_id = request.session['session_id']

    # Obtener el índice de la pregunta actual
    current_question_index = request.session['current_question']

    # Verificar límites para evitar IndexError
    if current_question_index >= len(all_questions):
        current_question_index = len(all_questions) - 1
        request.session['current_question'] = current_question_index

    # Verificar si es la última pregunta y todas están respondidas
    if 'next' in request.POST and current_question_index >= len(all_questions) - 1:
        if len(request.session['answers']) == len(all_questions):
            request.session['form_completed'] = True
            return redirect('results')
        else:
            # Redirigir a la primera pregunta sin responder
            for i, q in enumerate(all_questions):
                if str(q.id) not in request.session['answers']:
                    request.session['current_question'] = i
                    current_question_index = i
                    break

    # Obtener la pregunta actual, su tópico y opciones
    current_question = all_questions[current_question_index]
    current_topic = current_question.topic
    options = Option.objects.filter(question=current_question)

    if request.method == 'POST':
        selected_option = request.POST.get('option')

        # Validación para el botón "next"
        if 'next' in request.POST:
            if not selected_option and str(current_question.id) not in request.session['answers']:
                context = {
                    'question': current_question,
                    'topic': current_topic,
                    'options': options,
                    'progress': int(
                        (len(request.session['answers']) / len(all_questions)) * 100) if all_questions else 0,
                    'saved_answer': request.session['answers'].get(str(current_question.id), ''),
                    'has_previous': current_question_index > 0,
                    'has_next': current_question_index < len(all_questions) - 1,
                    'topic_scores': request.session.get('topic_scores', {}),
                    'current_index': current_question_index + 1,
                    'total_questions': len(all_questions),
                    'answered_questions': len(request.session['answers']),
                    'user_role': role_id,
                    'error_message': 'Por favor, seleccione una opción antes de continuar.'
                }
                return render(request, 'form/evaluate.html', context)

        if selected_option:
            try:
                option = Option.objects.get(id=selected_option)
                question_id = str(current_question.id)
                topic_name = current_topic.name

                # Actualizar respuestas y puntajes
                answers = request.session['answers']
                topic_scores = request.session['topic_scores']
                question_scores = request.session['question_scores']

                # Si ya existía una respuesta, restar el puntaje anterior
                if question_id in answers:
                    old_score = question_scores.get(question_id, 0)
                    topic_scores[topic_name] = topic_scores.get(topic_name, 0) - old_score

                    # Eliminar la respuesta anterior de la base de datos
                    Answer.objects.filter(
                        session_id=session_id,
                        question_id=current_question.id
                    ).delete()

                # Guardar nueva respuesta y puntaje
                answers[question_id] = selected_option
                question_scores[question_id] = option.score
                topic_scores[topic_name] = topic_scores.get(topic_name, 0) + option.score

                # Guardar la respuesta en la base de datos (modelo Answer)
                Answer.objects.create(
                    session_id=session_id,
                    question=current_question,
                    option=option
                )

                # Actualizar sesión
                request.session['answers'] = answers
                request.session['topic_scores'] = topic_scores
                request.session['question_scores'] = question_scores

                # Si se presiona finalizar, verificar que todas las preguntas estén respondidas
                if 'finish' in request.POST:
                    if len(answers) == len(all_questions):
                        request.session['form_completed'] = True
                        request.session.modified = True
                        return redirect('results')
                    else:
                        # Redirigir a la primera pregunta sin responder
                        for i, q in enumerate(all_questions):
                            if str(q.id) not in answers:
                                request.session['current_question'] = i
                                request.session.modified = True
                                return redirect('evaluate', role_id=role_id)

            except Option.DoesNotExist:
                logging.error(f"Option with ID {selected_option} not found")

        # Procesar navegación
        if 'next' in request.POST and current_question_index < len(all_questions) - 1:
            request.session['current_question'] += 1
        elif 'previous' in request.POST and current_question_index > 0:
            request.session['current_question'] -= 1

        request.session.modified = True
        return redirect('evaluate', role_id=role_id)

    # Recuperar respuesta guardada
    saved_answer = request.session['answers'].get(str(current_question.id), '')

    # Calcular progreso con validación para evitar división por cero
    progress = int((len(request.session['answers']) / len(all_questions)) * 100) if all_questions else 0

    context = {
        'question': current_question,
        'topic': current_topic,
        'options': options,
        'progress': progress,
        'saved_answer': saved_answer,
        'has_previous': current_question_index > 0,
        'has_next': current_question_index < len(all_questions) - 1,
        'topic_scores': request.session.get('topic_scores', {}),
        'current_index': current_question_index + 1,
        'total_questions': len(all_questions),
        'answered_questions': len(request.session['answers']),
        'user_role': role_id
    }

    return render(request, 'form/evaluate.html', context)


def results(request, role=None):
    try:
        # Obtener el rol de la sesión si no viene como parámetro
        role_id = role if role is not None else request.session.get('role_id')

        if not role_id:
            return redirect('index')  # Redirigir a página principal si no hay rol

        role_obj = get_object_or_404(Role, id=role_id)

        # Obtener el ID de sesión
        session_id = request.session.get('session_id')

        if not session_id:
            return redirect('generate_form', role_id=role_id)

        # Verificar respuestas guardadas en la base de datos
        answers_count = Answer.objects.filter(session_id=session_id).count()

        # Obtener todas las preguntas para este rol
        all_questions = Question.objects.filter(topic__role=role_obj)
        total_questions = all_questions.count()

        # Verificar si ya hay resultados guardados para esta sesión
        existing_results = TopicResult.objects.filter(session_id=session_id)

        if existing_results.exists():

            final_results = {}
            total_points = 0
            total_possible_points = 0

            for result in existing_results:
                max_points_per_topic = result.total_questions * 6
                points = (result.score * max_points_per_topic) / 100

                final_results[result.topic.name] = {
                    'score': round(result.score, 2),
                    'total_questions': result.total_questions,
                    'answered_questions': result.total_questions,
                    'level': result.level
                }
                total_points += points
                total_possible_points += max_points_per_topic

            average_total = round((total_points / total_possible_points) * 100, 2) if total_possible_points > 0 else 0

        else:
            # Verificar si tenemos respuestas para calcular resultados
            if answers_count == 0:
                # No hay respuestas en la base de datos, redirigir a evaluación
                return redirect('evaluate', role_id=role_id)

            # Si hay respuestas pero no resultados guardados, calcular y guardar los resultados
            # Obtener todas las respuestas para esta sesión
            all_answers = Answer.objects.filter(session_id=session_id)

            # Agrupar respuestas por tópico
            answers_by_topic = {}
            for answer in all_answers:
                topic = answer.question.topic
                if topic not in answers_by_topic:
                    answers_by_topic[topic] = []
                answers_by_topic[topic].append(answer)

            # Calcular resultados por tópico
            final_results = {}
            total_points = 0
            total_possible_points = 0

            # Obtener todos los tópicos para este rol
            topics = Topic.objects.filter(role=role_obj)

            for topic in topics:
                # Obtener todas las preguntas para este tópico
                questions_in_topic = Question.objects.filter(topic=topic)
                total_questions_in_topic = questions_in_topic.count()

                # Obtener respuestas para este tópico
                answers_in_topic = answers_by_topic.get(topic, [])
                answered_questions_count = len(answers_in_topic)

                # Calcular puntaje para este tópico
                topic_points = sum(answer.option.score for answer in answers_in_topic)
                max_points_possible = total_questions_in_topic * 6

                # Calcular porcentaje de score
                score_percentage = (topic_points / max_points_possible) * 100 if max_points_possible > 0 else 0

                # Determinar nivel
                level = determine_level(score_percentage)

                # Guardar resultado en la base de datos
                TopicResult.objects.create(
                    topic=topic,
                    session_id=session_id,
                    score=round(score_percentage, 2),
                    level=level,
                    total_questions=total_questions_in_topic
                )

                final_results[topic.name] = {
                    'score': round(score_percentage, 2),
                    'total_questions': total_questions_in_topic,
                    'answered_questions': answered_questions_count,
                    'level': level
                }

                total_points += topic_points
                total_possible_points += max_points_possible

            # Calcular promedio total
            average_total = round((total_points / total_possible_points) * 100, 2) if total_possible_points > 0 else 0

            # Marcar que el formulario está completo en la sesión
            request.session['form_completed'] = True
            request.session.modified = True

        # Determinar el nivel total
        total_level = determine_level(average_total)

        # Guardar información importante en la sesión para referencias futuras
        request.session['results_calculated'] = True
        request.session['average_total'] = average_total
        request.session['total_level'] = total_level
        request.session.modified = True

        context = {
            'results': final_results,
            'total_score': average_total,
            'user_role': role_id,
            'total_level': total_level,
            'answers_count': answers_count,
            'total_questions': total_questions,
            'role_name': role_obj.name
        }

        # Si se solicita formato PDF
        if request.GET.get('format') == 'pdf':
            return generar_pdf(request, 'form/results_pdf.html', context)

        return render(request, 'form/results.html', context)

    except Exception as e:
        logging.error(f"Error procesando resultados: {e}")
        # Obtener el ID de rol de la sesión
        role_id_from_session = request.session.get('role_id', 1)
        return redirect('evaluate', role_id=role_id_from_session)


def determine_level(percentage):
    if 0 <= percentage <= 16.66:
        return 'A1'
    elif percentage <= 33.33:
        return 'A2'
    elif percentage <= 50:
        return 'B1'
    elif percentage <= 66.66:
        return 'B2'
    elif percentage <= 83.33:
        return 'C1'
    else:
        return 'C2'