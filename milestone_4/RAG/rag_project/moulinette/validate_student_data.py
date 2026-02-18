from moulinette.models import StudentSearchResultsAndAnswer

def validate_student_data(
    student_data: StudentSearchResultsAndAnswer,
    max_context_length: int,
    k: int
) -> bool:
    is_valid = True
    if student_data.k > k:
        is_valid = False
        print(f"Student data has more than {k} sources")
    for search_result in student_data.search_results:
        if len(search_result.retrieved_sources) > k:
            is_valid = False
            print(f"Search result {search_result.question_id} has more than {k} sources")
            break
        for source in search_result.retrieved_sources:
            source_length = source.last_character_index - source.first_character_index
            # TODO: update, we should use the text_length of the text (as some summary of the text could be used)
            # source_length = source.text_length
            if source_length > max_context_length:
                # is_valid = False
                print(f"Source {source.file_path}[{source.first_character_index}:{source.last_character_index}] has a length of {source_length} which is more than the limit of {max_context_length} characters")
                # break
        if not is_valid:
            break
    print(f"Student data is valid: {is_valid}")
    return is_valid