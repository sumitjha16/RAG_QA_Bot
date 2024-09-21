import multiprocessing
from src import process_pdf


def worker(pdf_string, question, return_dict):
    try:
        result = process_pdf(pdf_string, question)
        return_dict['result'] = result
    except Exception as e:
        return_dict['error'] = str(e)


def run_in_process(pdf_string, question=None):
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    process = multiprocessing.Process(target=worker, args=(pdf_string, question, return_dict))
    process.start()
    process.join()

    if 'error' in return_dict:
        raise Exception(return_dict['error'])
    return return_dict['result']