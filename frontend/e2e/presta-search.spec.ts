import { test, expect } from "@playwright/test";

test.describe("PrestaSearch E2E", () => {
  test("homepage loads with search tab", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toHaveText("PrestaSearch");
    await expect(page.getByText("Trouvez un prestataire")).toBeVisible();
  });

  test("admin tab shows directory with seed prestataires", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Admin" }).click();
    await expect(page.getByText("Annuaire")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Ajouter un prestataire" })).toBeVisible();
    // Wait for prestataires to load
    await expect(page.getByText(/\d+ prestataires/)).toBeVisible();
  });

  test("add prestataire via admin form", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Admin" }).click();

    // Fill form
    await page.getByPlaceholder("Nom du prestataire").fill("E2E Test Plombier");
    await page
      .getByPlaceholder("Ex: Plomberie, Coiffure, Développement web...")
      .fill("Plomberie");
    await page
      .getByPlaceholder("Décrivez les services proposés")
      .fill("Plombier de test créé par Playwright");
    await page
      .getByPlaceholder("réparation, installation, dépannage (séparés par virgules)")
      .fill("test, e2e, plomberie");

    // Submit
    await page.getByRole("button", { name: "Ajouter le prestataire" }).click();

    // Wait for success message
    await expect(page.getByText("Prestataire ajouté avec succès !")).toBeVisible({
      timeout: 15_000,
    });
  });

  test("search for a prestataire and get results", async ({ page }) => {
    await page.goto("/");

    // Type search query
    await page
      .getByPlaceholder("Décrivez votre besoin...")
      .fill("j'ai une fuite sous mon évier");
    await page.getByRole("button", { name: "Envoyer" }).click();

    // Wait for results to appear (provider cards)
    await expect(page.getByText("Jean Dupont Plomberie")).toBeVisible({
      timeout: 30_000,
    });
  });
});
