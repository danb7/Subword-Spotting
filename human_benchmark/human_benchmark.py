import pandas as pd


def get_human_benchmark(type='multi'):
    '''
    type: multi or classification

    returns: accuracy of human and number of responses
    '''
    if type=='multi':
        scores_df = pd.read_excel(r'human_benchmark\Subword-Spotting quiz (Responses).xlsx', sheet_name=None)
        
    elif type=='classification':
        scores_df = pd.read_excel(r'human_benchmark\Subwords-Spotting classification quiz (Responses).xlsx', sheet_name=None) 
    else:
        raise Exception('type need to be multi or classification')
    
    all_scores = pd.Series(dtype='int')
    for form_name, form_df in scores_df.items():
        all_scores = pd.concat([all_scores, form_df['Score']])
    return {'mean_score': all_scores.mean()/100, 'N': len(all_scores)}