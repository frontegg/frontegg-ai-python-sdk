

from setuptools import setup, find_packages

setup(
    name='frontegg-ai-sdk',
    version='1.0.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    description='A Python SDK for interacting with Frontegg AI Agents.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Frontegg',
    author_email='support@frontegg.com',
    url='https://github.com/frontegg/frontegg-ai-python-sdk',
    install_requires=[
        'requests',
        'httpx',
        'anyio',
        'httpx-sse',
        'pydantic',
        'mcp',
        'crewai[tools]>=0.5.0',
        'mcpadapt>=0.1.3',
        'nest-asyncio',
    ],
) 