#!/usr/bin/env python

# if __name__ == '__main__':
#     from setup import install_requires
#     with open('requirements.txt', 'w') as fou:
#         fou.writelines(l + '\n' for l in install_requires)

if __name__ == '__main__':
    # indent = "\n    "
    with open('requirements.txt') as fin:
        install_requires = [l.strip() for l in fin.readlines() if l and l.strip()]

    with open('setup.template.py') as fin:
        setup_template = fin.read()

    with open('setup.py', 'w') as fou:
        # fou.write(setup_template.format(install_requires='\n' + indent.join(install_requires)))
        fou.write(setup_template.replace('"""install_requires"""', repr(install_requires)))
