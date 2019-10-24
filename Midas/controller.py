import docker
import click
import os


@click.command()
@click.argument('image')
def main(image):
    try:
        docker_img = client.images.get(image)
    except docker.errors.ImageNotFound:
        # find the location of the image
        docker_img = client.images.build(path=f"{os.getcwd()}/{image}/.")

    client.containers.run(
        docker_img[0],
        # ['python', 'main.py'] + args,
        "python main.py ./data/SacramentocrimeJanuary2006.csv testdb testcoll",
        network="databases_default",
    )


# build
# run
if __name__ == "__main__":
    client = docker.from_env()
    main()
