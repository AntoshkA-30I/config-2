import visualizer


#load_config
outputs = []
config = visualizer.load_config('config.ini')
outputs.append(config['visualization_path'])
outputs.append(config['repository_path'])
outputs.append(config['output_file'])
assert outputs == ['https://mermaid.live/', 'C:/Users/anton/Desktop/config-2/test/', 'C:/Users/anton/Desktop/config-2/output.txt']


#get_git_commits
outputs = []
outputs = visualizer.get_git_commits(config['repository_path'])
assert outputs == ['commit 84ee0e34ffc34c0485a7059a633b7c197c627282', 
    '84ee0e34ffc34c0485a7059a633b7c197c627282 Merge feature-branch into main', 'commit b92a70ee3abc9414123c9f2f8a4e0b16327e9740', 
    'b92a70ee3abc9414123c9f2f8a4e0b16327e9740 Update file1.txt in main branch', 'commit 38cf36c02103f9dc4b37076c4f1f65dc380dfebe', 
    '38cf36c02103f9dc4b37076c4f1f65dc380dfebe Update file2.txt in feature-branch', 'commit 99c85937cdc928821561035399d6a9ac4fac68fa', 
    '99c85937cdc928821561035399d6a9ac4fac68fa update 4.txt', 'commit da84e54827f0286927fb344a3618e96573749612', 
    'da84e54827f0286927fb344a3618e96573749612 add folder3 and 5.txt', 'commit 277adc22cc79cee7a279bbc34326b434e8aabcc3', 
    '277adc22cc79cee7a279bbc34326b434e8aabcc3 update 1.txt', 'commit 66e0e1ac0e84ecee821e931ef7dfea3c437b6f72', '66e0e1ac0e84ecee821e931ef7dfea3c437b6f72 Initial commit']


#get_files_from_commit
outputs = []
outputs = visualizer.get_files_from_commit('b92a70ee3abc9414123c9f2f8a4e0b16327e9740 Update file1.txt in main branch', config['repository_path'])
assert outputs == ['1.txt']

outputs = []
outputs = visualizer.get_files_from_commit('da84e54827f0286927fb344a3618e96573749612 add folder3 and 5.txt', config['repository_path'])
assert outputs == ['folder3/5.txt']

outputs = []
outputs = visualizer.get_files_from_commit('66e0e1ac0e84ecee821e931ef7dfea3c437b6f72 Initial commit', config['repository_path'])
assert outputs == []


#build_mermaid_graph
outputs = []
outputs = visualizer.build_mermaid_graph(config['repository_path'])
assert outputs == ['graph TD', '    commit(84ee0e34ffc34c0485a7059a633b7c197c627282: No files)', 
    '    84ee0e34ffc34c0485a7059a633b7c197c627282(Merge feature-branch into main: No files)', 
    '    b92a70ee3abc9414123c9f2f8a4e0b16327e9740 --> 84ee0e34ffc34c0485a7059a633b7c197c627282', 
    '    38cf36c02103f9dc4b37076c4f1f65dc380dfebe --> 84ee0e34ffc34c0485a7059a633b7c197c627282', 
    '    b92a70ee3abc9414123c9f2f8a4e0b16327e9740(Update file1.txt in main branch: 1.txt)', 
    '    99c85937cdc928821561035399d6a9ac4fac68fa --> b92a70ee3abc9414123c9f2f8a4e0b16327e9740', 
    '    38cf36c02103f9dc4b37076c4f1f65dc380dfebe(Update file2.txt in feature-branch: 2.txt)', 
    '    99c85937cdc928821561035399d6a9ac4fac68fa --> 38cf36c02103f9dc4b37076c4f1f65dc380dfebe', 
    '    99c85937cdc928821561035399d6a9ac4fac68fa(update 4.txt: folder2/4.txt)', 
    '    da84e54827f0286927fb344a3618e96573749612 --> 99c85937cdc928821561035399d6a9ac4fac68fa', 
    '    da84e54827f0286927fb344a3618e96573749612(add folder3 and 5.txt: folder3/5.txt)', 
    '    277adc22cc79cee7a279bbc34326b434e8aabcc3 --> da84e54827f0286927fb344a3618e96573749612', 
    '    277adc22cc79cee7a279bbc34326b434e8aabcc3(update 1.txt: 1.txt)', 
    '    66e0e1ac0e84ecee821e931ef7dfea3c437b6f72 --> 277adc22cc79cee7a279bbc34326b434e8aabcc3', 
    '    66e0e1ac0e84ecee821e931ef7dfea3c437b6f72(Initial commit: No files)']


print('OK')